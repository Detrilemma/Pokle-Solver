"""Pokle game solver for finding valid poker table runouts.

This module contains the core Solver class that exhaustively searches for all
possible table configurations (flop, turn, river) matching specified hand
ranking constraints across three players. Uses optimized hand evaluation,
entropy-based guess selection, and vectorized comparison operations.

Classes:
    HandRanking: Dataclass for poker hand evaluation results
    PhaseEvaluation: Dataclass for phase validation configuration
    Solver: Main solver class for finding valid tables
"""

import os

# ARM64 LLVM optimization workaround
# Use generic ARM64 target to avoid CPU-specific scheduling model bugs
os.environ["NUMBA_CPU_NAME"] = "generic"

from .card import Card, ColorCard, RANK_MIN, RANK_MAX, VALID_SUITS as SUITS
from itertools import combinations
from scipy.stats import entropy
from dataclasses import dataclass
from typing import Optional, Sequence, Iterable, Iterator
from numba import guvectorize, int8, int16
import numpy as np
import polars as pl


# Constants for hand rankings
HAND_RANK_HIGH_CARD = 1
HAND_RANK_PAIR = 2
HAND_RANK_TWO_PAIR = 3
HAND_RANK_THREE_KIND = 4
HAND_RANK_STRAIGHT = 5
HAND_RANK_FLUSH = 6
HAND_RANK_FULL_HOUSE = 7
HAND_RANK_FOUR_KIND = 8
HAND_RANK_STRAIGHT_FLUSH = 9

# Card rank constants (also available from card module)
RANK_ACE = 14
RANK_KING = 13
RANK_QUEEN = 12
RANK_JACK = 11
RANK_TEN = 10

# Color constants
COLOR_GREY = "e"
COLOR_YELLOW = "y"
COLOR_GREEN = "g"
VALID_COLORS = [COLOR_GREY, COLOR_YELLOW, COLOR_GREEN]

# Number of players
NUM_PLAYERS = 3
HOLE_CARDS_PER_PLAYER = 2

# Table size constants
FLOP_SIZE = 3
TURN_SIZE = 4
RIVER_SIZE = 5


@dataclass
class HandRanking:
    """Result of evaluating a poker hand.

    Represents the strength of a poker hand with sufficient information to
    determine winners in showdowns. Used for comparing hands and determining
    which player has the best hand at each game phase.

    Attributes:
        rank (int): Numerical rank of hand type (1=high card, 2=pair, 3=two pair,
                   4=three of a kind, 5=straight, 6=flush, 7=full house,
                   8=four of a kind, 9=straight flush)
        tie_breakers (tuple): Tuple of card ranks for breaking ties between hands
                             of the same type, ordered by importance
        best_hand (tuple): The 5 Card objects that form the best possible hand
    """

    rank: int  # Numerical rank (1=high card, 2=pair, ..., 9=straight flush)
    tie_breakers: tuple  # Tuple of ranks for tie-breaking
    best_hand: tuple  # Tuple of Card objects in the best 5-card hand


@dataclass
class PhaseEvaluation:
    """Configuration for evaluating a poker game phase (flop, turn, or river).

    Contains all information needed to evaluate whether a specific table state
    matches the expected hand rankings for a given phase of the game.
    Used internally by the Solver to validate candidate table configurations.

    Attributes:
        table (list): The table state to evaluate (list of Card objects)
        expected_rankings (list): Expected hand strength rankings for each player
                                 (list of 3 integers, permutation of [1, 2, 3])
        prev_cards_used (set | None): Set of cards already used in previous phases
        validate_all_cards_used (bool): Whether to check all cards are from the deck

    Examples:
        >>> phase = PhaseEvaluation(
        ...     table=[Card(10, 'H'), Card(14, 'D'), Card(7, 'S')],
        ...     expected_rankings=[2, 1, 3],  # P2 best, P1 second, P3 worst
        ...     prev_cards_used=set()
        ... )
    """

    table: list
    expected_rankings: list
    prev_cards_used: Optional[set] = None
    validate_all_cards_used: bool = False


MASTER_DECK = [
    Card(rank, suit) for rank in range(RANK_MIN, RANK_MAX + 1) for suit in SUITS
]


class Solver:
    """Solves for valid poker table runouts given player hole cards and hand rankings.

    The Solver finds all possible table configurations (flop + turn + river) that
    maintain specified hand strength rankings for each phase of the game. This is
    the core engine for the Pokle game, which challenges players to guess the table
    based on hand ranking feedback.

    Key features:
    - Finds all valid table runouts matching ranking constraints
    - Calculates optimal guesses using Shannon entropy
    - Supports interactive guessing with color-coded feedback
    - Handles datasets from small (hundreds) to large (thousands) of possible tables

    The solver uses three-player Texas Hold'em rules and validates that hand rankings
    are consistent across all three phases (flop, turn, river).

    Attributes:
        hole_cards (dict): Player hole cards {'P1': [Card, Card], 'P2': ..., 'P3': ...}
        flop_hand_ranks (list): Expected rankings for flop phase [2, 1, 3]
        turn_hand_ranks (list): Expected rankings for turn phase [1, 2, 3]
        river_hand_ranks (list): Expected rankings for river phase [1, 2, 3]
        valid_tables (list): All valid complete table states found by solve()

    Examples:
        >>> # Setup solver with player hands and expected rankings
        >>> solver = Solver(
        ...     p1hole=[Card.from_string('AH'), Card.from_string('KH')],
        ...     p2hole=[Card.from_string('10D'), Card.from_string('10C')],
        ...     p3hole=[Card.from_string('7S'), Card.from_string('2S')],
        ...     flop_hand_ranks=[2, 1, 3],   # P2 best at flop
        ...     turn_hand_ranks=[1, 2, 3],   # P1 best at turn
        ...     river_hand_ranks=[1, 2, 3]   # P1 best at river
        ... )

        >>> # Find all valid tables
        >>> possible_rivers = solver.solve()
        >>> print(f"Found {len(possible_rivers)} possible tables")

        >>> # Get optimal first guess (using entropy)
        >>> best_guess = solver.get_maxh_table()
        >>> solver.print_game(best_guess)

        >>> # Interactive guessing loop
        >>> feedback = ['g', 'y', 'e', 'e', 'y']  # Green/yellow/grey
        >>> solver.next_table_guess(feedback)
        >>> next_guess = solver.get_maxh_table()
    """

    def __init__(
        self,
        p1hole: list,
        p2hole: list,
        p3hole: list,
        flop_hand_ranks: list,
        turn_hand_ranks: list,
        river_hand_ranks: list,
    ):
        # Validate hole cards
        for p_name, p_hole in zip(["P1", "P2", "P3"], [p1hole, p2hole, p3hole]):
            if (
                not isinstance(p_hole, list)
                or len(p_hole) != HOLE_CARDS_PER_PLAYER
                or not all(isinstance(card, Card) for card in p_hole)
            ):
                raise ValueError(
                    f"{p_name} hole cards must be a list of exactly {HOLE_CARDS_PER_PLAYER} Card objects."
                )

        # Updated validation for hand ranks
        expected_ranks = list(range(1, NUM_PLAYERS + 1))
        for hand_rank_lists in [flop_hand_ranks, turn_hand_ranks, river_hand_ranks]:
            if (
                not isinstance(hand_rank_lists, list)
                or sorted(hand_rank_lists) != expected_ranks
            ):
                raise ValueError(
                    f"Hand rank lists must be a permutation of {expected_ranks}"
                )

        self.hole_cards = {"P1": p1hole, "P2": p2hole, "P3": p3hole}

        self.flop_hand_ranks = flop_hand_ranks
        self.turn_hand_ranks = turn_hand_ranks
        self.river_hand_ranks = river_hand_ranks

        self.current_deck = MASTER_DECK.copy()
        self.__valid_tables = []
        self.__maxh_table = []
        self.__used_tables = []
        self.__print_maxh_table = []
        self.__current_colors = []
        self.__compared_tables = pl.LazyFrame()
        self.__rivers_dict = dict()
        # Cache all hole cards set for performance (used in __evaluate_phase)
        self.__all_hole_cards = {
            card for hole in self.hole_cards.values() for card in hole
        }

    @property
    def valid_tables(self) -> list[list[Card]]:
        """Get the list of valid river tables found by solve().

        Returns:
            list: List of list[Card] representing all valid complete tables.

        Examples:
            >>> solver.solve()
            >>> len(solver.valid_tables)
            412
        """
        return self.__valid_tables

    @staticmethod
    def __rank_hand(table: list[Card], hole: list[Card]) -> HandRanking:
        """Evaluate the best 5-card poker hand from hole cards and table cards.

        Args:
            table (list): List of Card objects on the table (3-5 cards).
            hole (list): List of 2 Card objects (player's hole cards).

        Returns:
            HandRanking: Dataclass containing:
                - rank (int): Hand type (1=high card ... 9=straight flush)
                - tie_breakers (tuple): Ranks for breaking ties
                - best_hand (tuple): Best 5 Card objects

        Examples:
            >>> table = [Card(10, 'H'), Card(11, 'H'), Card(12, 'H')]
            >>> hole = [Card(13, 'H'), Card(14, 'H')]
            >>> ranking = Solver.__rank_hand(table, hole)
            >>> ranking.rank
            9  # Straight flush
            >>> ranking.tie_breakers
            (14,)  # Ace-high
        """
        cards = hole + list(table)

        # Count occurrences of each rank and group cards by suit in single pass
        rank_groups = {}
        suit_groups = {}

        for card in cards:
            rank = card.rank
            suit = card.suit

            if rank in rank_groups:
                rank_groups[rank].append(card)
            else:
                rank_groups[rank] = [card]

            if suit in suit_groups:
                suit_groups[suit].append(card)
            else:
                suit_groups[suit] = [card]

        # Check for flush
        flush_cards = None
        for suited_cards in suit_groups.values():
            if len(suited_cards) >= 5:
                # Sort flush cards by rank descending
                flush_cards = sorted(suited_cards, key=lambda c: c.rank, reverse=True)
                break

        # Check for straight
        unique_ranks = sorted(rank_groups.keys(), reverse=True)
        straight_high_card = None

        # Standard straight check
        for i in range(len(unique_ranks) - 4):
            if unique_ranks[i] - unique_ranks[i + 4] == 4:
                straight_high_card = unique_ranks[i]
                break

        # Special case for A-5-4-3-2 (Ace low straight)
        if not straight_high_card and RANK_ACE in rank_groups and 5 in rank_groups:
            if all(r in rank_groups for r in (2, 3, 4)):
                straight_high_card = 5

        # Check for straight flush
        if flush_cards and straight_high_card:
            flush_ranks_set = {c.rank for c in flush_cards}

            # Check if the straight exists in the flush cards
            if straight_high_card == 5:
                # Ace-low straight flush
                if all(r in flush_ranks_set for r in (RANK_ACE, 5, 4, 3, 2)):
                    best_hand = [
                        c for c in flush_cards if c.rank in (RANK_ACE, 5, 4, 3, 2)
                    ]
                    best_hand.sort(
                        key=lambda c: (1 if c.rank == RANK_ACE else c.rank),
                        reverse=True,
                    )
                    return HandRanking(
                        HAND_RANK_STRAIGHT_FLUSH, (5,), tuple(best_hand[:5])
                    )
            else:
                # Regular straight flush
                if all(
                    r in flush_ranks_set
                    for r in range(straight_high_card - 4, straight_high_card + 1)
                ):
                    best_hand = [
                        c
                        for c in flush_cards
                        if straight_high_card >= c.rank >= straight_high_card - 4
                    ]
                    return HandRanking(
                        HAND_RANK_STRAIGHT_FLUSH,
                        (straight_high_card,),
                        tuple(best_hand[:5]),
                    )

        # Pre-compute group sizes
        three_ranks = []
        pair_ranks = []
        four_rank = None

        for rank, group in rank_groups.items():
            group_len = len(group)
            if group_len == 4:
                four_rank = rank
                break
            elif group_len == 3:
                three_ranks.append(rank)
            elif group_len == 2:
                pair_ranks.append(rank)

        # Check for four of a kind
        if four_rank is not None:
            return HandRanking(
                HAND_RANK_FOUR_KIND, (four_rank,), tuple(rank_groups[four_rank])
            )

        # Check for full house
        if (three_ranks and pair_ranks) or len(three_ranks) > 1:
            max_three = max(three_ranks)
            three_of_a_kind = rank_groups[max_three]

            if pair_ranks:
                max_pair_rank = max(pair_ranks)
                pair = rank_groups[max_pair_rank]
            else:
                min_three = min(three_ranks)
                pair = rank_groups[min_three][:2]
                max_pair_rank = min_three

            best_hand = three_of_a_kind + pair
            return HandRanking(
                HAND_RANK_FULL_HOUSE, (max_three, max_pair_rank), tuple(best_hand)
            )

        # Check for flush
        if flush_cards:
            flush_card_hand = flush_cards[:5]
            flush_card_hand_ranks = tuple(c.rank for c in flush_card_hand)
            return HandRanking(
                HAND_RANK_FLUSH, flush_card_hand_ranks, tuple(flush_card_hand)
            )

        # Check for straight
        if straight_high_card:
            if straight_high_card == 5:
                best_hand = [c for c in cards if c.rank in (RANK_ACE, 5, 4, 3, 2)]
                best_hand.sort(
                    key=lambda c: (1 if c.rank == RANK_ACE else c.rank), reverse=True
                )
            else:
                best_hand = [
                    c
                    for c in cards
                    if straight_high_card >= c.rank >= straight_high_card - 4
                ]
                best_hand.sort(reverse=True)
            return HandRanking(
                HAND_RANK_STRAIGHT, (straight_high_card,), tuple(best_hand[:5])
            )

        # Check for three of a kind
        if three_ranks:
            max_three = max(three_ranks)
            three_of_a_kind = rank_groups[max_three]
            remaining = sorted(set(cards) - set(three_of_a_kind), reverse=True)
            remaining_ranks = [c.rank for c in remaining[:2]]
            return HandRanking(
                HAND_RANK_THREE_KIND,
                tuple([max_three] + remaining_ranks),
                tuple(three_of_a_kind),
            )

        # Check for two pair
        if len(pair_ranks) >= 2:
            pair_ranks.sort(reverse=True)
            two_pair = rank_groups[pair_ranks[0]] + rank_groups[pair_ranks[1]]
            remaining = sorted(set(cards) - set(two_pair), reverse=True)
            remaining_rank = remaining[0].rank if remaining else 0
            return HandRanking(
                HAND_RANK_TWO_PAIR,
                tuple([pair_ranks[0], pair_ranks[1], remaining_rank]),
                tuple(two_pair),
            )

        # Check for one pair
        if pair_ranks:
            pair_rank = pair_ranks[0]
            pair = rank_groups[pair_rank]
            remaining = sorted(set(cards) - set(pair), reverse=True)
            remaining_ranks = [c.rank for c in remaining[:3]]
            return HandRanking(
                HAND_RANK_PAIR, tuple([pair_rank] + remaining_ranks), tuple(pair)
            )

        # High card
        best_hand = sorted(cards, reverse=True)[:5]
        best_hand_ranks = tuple(c.rank for c in best_hand)
        return HandRanking(
            HAND_RANK_HIGH_CARD,
            best_hand_ranks,
            tuple([best_hand[0]]),
        )

    def __possible_flops(self) -> Iterator[tuple[list[Card], set[Card]]]:
        """Find all possible flops that maintain the current player rankings.

        Yields:
            tuple: (table, cards_used_in_hands) where cards_used_in_hands
                  is a set of table cards used in any player's best hand at the flop.
        """
        hole_cards = {card for hole in self.hole_cards.values() for card in hole}
        remaining_cards = set(self.current_deck).difference(hole_cards)
        self.current_deck = list(remaining_cards)

        all_flops = combinations(self.current_deck, FLOP_SIZE)

        for flop in all_flops:
            flop_table = list(flop)

            phase_eval = PhaseEvaluation(
                table=flop_table, expected_rankings=self.flop_hand_ranks
            )
            is_valid, cards_used = self.__evaluate_phase(phase_eval)

            if is_valid:
                yield (flop_table, cards_used)

    def __evaluate_phase(self, phase_eval: PhaseEvaluation) -> tuple[bool, set[Card]]:
        """Helper method to evaluate hands for all players at a given phase.

        Args:
            phase_eval (PhaseEvaluation): Configuration object containing table, rankings,
                                           and validation parameters.

        Returns:
            tuple: (is_valid, cards_used_accumulated) where is_valid indicates if this table
                   matches expected rankings, and cards_used_accumulated is the set of all
                   cards used across phases.
        """
        # Use cached hole cards set instead of recreating 412K times
        all_hole_cards = self.__all_hole_cards

        # Rank hands and collect results incrementally with early rejection
        current_player_ranks = []
        cards_used_current_phase = set()

        # Track min/max ranks seen so far for early rejection
        min_rank_seen = float("inf")
        max_rank_seen = float("-inf")

        for player, hole in self.hole_cards.items():
            # Compute hand rank for this player
            player_hand = Solver.__rank_hand(phase_eval.table, hole)
            rank = player_hand.rank
            tie_breakers = player_hand.tie_breakers

            current_player_ranks.append(
                (player, rank, tie_breakers, player_hand.best_hand)
            )

            # Early rejection: Check if we can already determine there will be ties
            # If we've seen 2 players and they have identical (rank, tie_breakers), reject immediately
            if len(current_player_ranks) >= 2:
                # Check if current player ties with any previous player
                current_comparator = (rank, tie_breakers)
                for prev_player in current_player_ranks[:-1]:
                    if (prev_player[1], prev_player[2]) == current_comparator:
                        # Found a tie - reject immediately without evaluating remaining players
                        return False, set()

            # Track rank range for additional early rejection opportunities
            min_rank_seen = min(min_rank_seen, rank)
            max_rank_seen = max(max_rank_seen, rank)

            # Collect cards used in current phase (exclude flush hands)
            if rank != HAND_RANK_FLUSH:  # Not a flush
                cards_used_current_phase.update(set(player_hand.best_hand))

        # Accumulate cards used across all phases
        if phase_eval.prev_cards_used is not None:
            cards_used_accumulated = (
                phase_eval.prev_cards_used | cards_used_current_phase
            )
        else:
            cards_used_accumulated = cards_used_current_phase

        cards_used_accumulated.difference_update(all_hole_cards)

        # For river, validate that all table cards were used at some point
        if phase_eval.validate_all_cards_used and cards_used_accumulated != set(
            phase_eval.table
        ):
            return False, cards_used_accumulated

        # Sort by rank and tie breakers
        current_player_ranks.sort(reverse=True, key=lambda x: (x[1], x[2]))

        # Map player names to their rankings (1=best, 2=second, 3=third)
        current_player_ranks_comparable = [
            int(player[0][1]) for player in current_player_ranks
        ]

        is_valid = current_player_ranks_comparable == phase_eval.expected_rankings
        return is_valid, cards_used_accumulated

    def __find_valid_next_phase(
        self,
        prev_phase_results: Iterable[tuple[list[Card], set[Card]]],
        expected_rankings: list[int],
        validate_all_cards_used: bool = False,
    ) -> Iterator[tuple[list[Card], set[Card]]]:
        """Helper method to find valid tables for the next phase (turn or river).

        Args:
            prev_phase_results: Iterator of tuples (table, cards_used) from previous phase.
            expected_rankings (list): Expected hand rankings for this phase.
            validate_all_cards_used (bool): Whether to validate all cards were used.

        Yields:
            tuple: (table, cards_used_accumulated) for valid combinations.
        """
        for prev_table, prev_cards_used in prev_phase_results:
            remaining_deck = set(self.current_deck) - set(prev_table)

            for next_card in remaining_deck:
                next_table = prev_table + [next_card]

                phase_eval = PhaseEvaluation(
                    table=next_table,
                    expected_rankings=expected_rankings,
                    prev_cards_used=prev_cards_used,
                    validate_all_cards_used=validate_all_cards_used,
                )
                is_valid, cards_used = self.__evaluate_phase(phase_eval)

                if is_valid:
                    yield (next_table, cards_used)

    def __possible_turns(
        self, flops: Iterable[tuple[list[Card], set[Card]]]
    ) -> Iterator[tuple[list[Card], set[Card]]]:
        """Find all possible turns that maintain the current player rankings.

        Args:
            flops: Iterator of tuples (table, cards_used) from flop phase.

        Yields:
            tuple: (table, cards_used_accumulated) for valid turn combinations.
        """
        return self.__find_valid_next_phase(flops, self.turn_hand_ranks)

    def __possible_rivers(
        self, turns: Iterable[tuple[list[Card], set[Card]]]
    ) -> Iterator[tuple[list[Card], set[Card]]]:
        """Find all possible rivers that maintain the current player rankings.

        Args:
            turns: Iterator of tuples (table, cards_used) from turn phase.

        Yields:
            tuple: (table, cards_used_accumulated) for valid river combinations.
        """
        return self.__find_valid_next_phase(
            turns, self.river_hand_ranks, validate_all_cards_used=True
        )

    @staticmethod
    @guvectorize(
        [(int8[:, :], int8[:, :], int16[:])],  # type signature: 2D inputs, 1D output
        "(n,m),(n,m)->(n)",  # shape signature: batch processing
        nopython=True,
    )
    def __compare_tables(guess_indices, answer_indices, result):
        """Compare batches of poker tables and return color-coded results.

        Args:
            guess_indices: 2D array of shape (n, 5) - n tables with 5 cards each
            answer_indices: 2D array of shape (n, 5) - n tables with 5 cards each
            result: 1D output array of shape (n,) - encoded color codes for each table
        """
        n_tables = guess_indices.shape[0]
        for table_idx in range(n_tables):
            guess_table = guess_indices[table_idx]
            guess_ranks = guess_table // 4
            guess_suits = guess_table % 4
            answer_table = answer_indices[table_idx]
            answer_ranks = answer_table // 4
            answer_suits = answer_table % 4
            flop_answer_ranks = answer_ranks[:FLOP_SIZE]
            flop_answer_suits = answer_suits[:FLOP_SIZE]
            answer_flop = answer_table[:FLOP_SIZE]

            colors = [0, 0, 0, 0, 0]  # default to grey
            for i in range(FLOP_SIZE):
                if guess_table[i] in answer_flop:
                    colors[i] = 2  # green
                    answer_i = np.flatnonzero(answer_flop == guess_table[i])[0]
                    flop_answer_ranks[answer_i] = -1  # mark as used
                    flop_answer_suits[answer_i] = -1  # mark as used
                elif (
                    guess_ranks[i] in flop_answer_ranks
                    or guess_suits[i] in flop_answer_suits
                ):
                    colors[i] = 1  # yellow
                else:
                    colors[i] = 0  # grey

            for i in range(FLOP_SIZE, RIVER_SIZE):
                if guess_table[i] == answer_table[i]:
                    colors[i] = 2  # green
                elif (
                    guess_ranks[i] == answer_ranks[i]
                    or guess_suits[i] == answer_suits[i]
                ):
                    colors[i] = 1  # yellow
                else:
                    colors[i] = 0  # grey

            place_multiplier = 100_000
            result_value = 0
            for color in colors:
                place_multiplier //= 10
                result_value += color * place_multiplier

            result[table_idx] = result_value

    def __organize_flop(self, table: list[Card]) -> list[Card | None]:
        """
        Organize flop cards based on matching priority with the previous table.

        This method reorders the first three cards (flop) of the current table to align
        with the previous table's flop based on a priority system: exact card matches
        take highest priority, followed by rank matches, then suit matches, and finally
        any remaining cards fill leftover slots. The turn and river cards (positions 4-5)
        are preserved unchanged.

        Args:
            table (list): A list of Card objects representing the current community cards,
                          where the first three elements are the flop.

        Returns:
            list: A new list with the reorganized flop (first 3 positions) based on
                  matching priorities, followed by the unchanged turn and river cards.

        Note:
            This method requires that __used_tables contains at least one previous table
            to compare against.
        """
        preceding_flop = self.__used_tables[-1][:FLOP_SIZE].copy()
        current_flop = table[:FLOP_SIZE].copy()
        updated_flop: list[Card | None] = [None] * FLOP_SIZE

        # Phase 1: Exact card matches (highest priority)
        for i, prev_card in enumerate(preceding_flop):
            if prev_card in current_flop:
                updated_flop[i] = prev_card
                current_flop.remove(prev_card)
                preceding_flop[i] = None  # Mark as matched

        # Phase 2: Rank matches (second priority)
        for i, prev_card in enumerate(preceding_flop):
            if prev_card is None or updated_flop[i] is not None:
                continue

            match_idx = next(
                (
                    j
                    for j, curr_card in enumerate(current_flop)
                    if curr_card.rank == prev_card.rank
                ),
                None,
            )
            if match_idx is not None:
                updated_flop[i] = current_flop.pop(match_idx)

        # Phase 3: Suit matches (third priority)
        for i, prev_card in enumerate(preceding_flop):
            if prev_card is None or updated_flop[i] is not None:
                continue

            match_idx = next(
                (
                    j
                    for j, curr_card in enumerate(current_flop)
                    if curr_card.suit == prev_card.suit
                ),
                None,
            )
            if match_idx is not None:
                updated_flop[i] = current_flop.pop(match_idx)

        # Phase 4: Fill remaining slots with leftover cards
        for i in range(FLOP_SIZE):
            if updated_flop[i] is None:
                if current_flop:
                    updated_flop[i] = current_flop.pop(0)
                else:
                    raise ValueError(
                        "Not enough cards to fill flop"
                    )  # Fail fast if logic is wrong

        return updated_flop + table[FLOP_SIZE:]

    def get_maxh_table(self, use_sampling: bool = True) -> Sequence[Card | None]:
        """Calculate the table with highest entropy from all possible rivers.

        For large river sets (>1000), uses sampling to approximate entropy efficiently.
        For small sets, computes exact entropy.

        Args:
            use_sampling (bool): Force sampling on/off. Defaults to True.

        Returns:
            Sequence[Card | None]: The river with the highest entropy. May contain None values.
        """
        # Validate state
        if not getattr(self, "_Solver__valid_tables", None):
            raise ValueError("No possible rivers calculated. Please run solve() first.")

        rivers = self.__valid_tables

        rivers_str = [" ".join(str(card) for card in river) for river in rivers]
        rivers_index = [[card.card_index for card in river] for river in rivers]

        self.__rivers_dict = dict(zip(rivers_str, rivers))

        rivers_df = pl.DataFrame(
            {"rivers_str": rivers_str, "rivers_index": rivers_index},
            schema={"rivers_str": pl.Utf8, "rivers_index": pl.Array(pl.Int8, 5)},
        )
        rivers_lf = rivers_df.lazy()

        if use_sampling and len(rivers) > 50:
            sampled_rivers_lf = rivers_df.sample(n=50, with_replacement=False).lazy()
            self.__compared_tables = sampled_rivers_lf.join(
                rivers_lf, how="cross", suffix="_answer"
            )
        else:
            self.__compared_tables = rivers_lf.join(
                rivers_lf, how="cross", suffix="_answer"
            )

        # For Array columns, we need to convert to numpy arrays for guvectorize
        self.__compared_tables = self.__compared_tables.with_columns(
            pl.struct(["rivers_index", "rivers_index_answer"])
            .map_batches(
                lambda batch: pl.Series(
                    "comparison",
                    Solver.__compare_tables(  # type: ignore
                        batch.struct.field("rivers_index")
                        .to_numpy()
                        .reshape(-1, 5)
                        .astype(np.int8),
                        batch.struct.field("rivers_index_answer")
                        .to_numpy()
                        .reshape(-1, 5)
                        .astype(np.int8),
                    ),
                ),
                return_dtype=pl.Int16,
            )
            .alias("comparison")
        )

        # Groups by guess river string and aggregates comparison results into lists
        rivers_grouped = self.__compared_tables.group_by("rivers_str").agg(
            pl.col("comparison").alias("comparison_list")
        )

        # Calculate probabilities of each comparison result
        rivers_grouped = rivers_grouped.with_columns(
            pl.col("comparison_list")
            .list.eval(
                pl.element().value_counts(normalize=True).struct.field("proportion")
            )
            .list.eval(
                pl.element().map_batches(
                    lambda s: entropy(s, base=2),
                    returns_scalar=True,
                    return_dtype=pl.Float64,
                )
            )
            .list.first()
            .alias("entropy")
        )
        entropy_df = rivers_grouped.select(["rivers_str", "entropy"]).collect()
        max_entropy_river = (
            entropy_df.filter(pl.col("entropy") == pl.col("entropy").max())
            .select("rivers_str")
            .row(0)[0]
        )

        self.__maxh_table = self.__rivers_dict[max_entropy_river]

        if self.__used_tables:
            self.__print_maxh_table = self.__organize_flop(self.__maxh_table)
        else:
            self.__print_maxh_table = self.__maxh_table.copy()

        return self.__print_maxh_table

    def next_table_guess(self, table_colors: list[str]) -> list[list[Card]]:
        """Filter valid rivers based on color feedback from the current guess.

        Updates the internal list of valid rivers to only include those that
        would produce the given color pattern for the current guess. This is
        used in the interactive guessing loop.

        Args:
            table_colors (list): List of 5 color strings for each card:
                                'g' = green, 'y' = yellow, 'e' = grey.
            current_guess (list, optional): The table being guessed (5 cards). Defaults to maxh_table.

        Returns:
            list: Filtered list of valid rivers matching the color feedback.

        Raises:
            ValueError: If solve() hasn't been called, guess is invalid, or colors malformed.

        Examples:
            >>> solver.solve()
            >>> guess = solver.get_maxh_table()
            >>> # User sees green, yellow, grey, grey, yellow
            >>> remaining = solver.next_table_guess(['g', 'y', 'e', 'e', 'y'], guess)
            >>> len(remaining)
            87
        """
        # Validate state

        if not self.__maxh_table:
            raise ValueError(
                "No current guess available. Please run get_maxh_table() first."
            )

        current_guess = self.__maxh_table

        if not getattr(self, "_Solver__valid_tables", None):
            raise ValueError("No possible rivers calculated. Please run solve() first.")
        if not isinstance(current_guess, list) or len(current_guess) != RIVER_SIZE:
            raise ValueError(
                f"Current guess must be a list of {RIVER_SIZE} Card objects (complete table)."
            )
        if not isinstance(table_colors, list) or len(table_colors) != RIVER_SIZE:
            raise ValueError(
                f"Table colors must be a list of {RIVER_SIZE} colors for each card in the table."
            )

        # Validate internal compared tables before filtering
        # Use explicit `is None` check to avoid evaluating a LazyFrame in boolean context
        if getattr(self, "_Solver__compared_tables", None) is None:
            raise ValueError(
                "Comparison table not initialized. Call get_maxh_table() before next_table_guess()."
            )

        comp_tables = self.__compared_tables
        if not isinstance(comp_tables, pl.LazyFrame):
            raise TypeError("Internal __compared_tables must be a polars LazyFrame.")

        # Safely obtain column names; collecting a LazyFrame is used only as a fallback
        try:
            # Use collect_schema().names() to read column names without full collection
            cols = comp_tables.collect_schema().names()
        except Exception:
            # Fallback: collect the frame and read columns (more expensive)
            cols = list(comp_tables.collect().columns)

        required_cols = {"rivers_str", "comparison", "rivers_str_answer"}
        missing = required_cols - set(cols)
        if missing:
            raise ValueError(
                f"__compared_tables missing required columns: {sorted(missing)}"
            )

        self.__current_colors = table_colors.copy()

        # reorder the colors to match the internal representation
        if self.__used_tables:
            color_map = dict(zip(self.__print_maxh_table, table_colors))
            table_colors = [color_map[card] for card in current_guess]

        color_int_dict = {"e": 0, "y": 1, "g": 2}
        place_multiplier = 100_000
        result_value = 0
        for color in table_colors:
            place_multiplier //= 10
            result_value += color_int_dict[color] * place_multiplier

        guess_str = " ".join(str(card) for card in current_guess)

        compared_tables = self.__compared_tables.filter(
            (pl.col("rivers_str") == guess_str) & (pl.col("comparison") == result_value)
        )
        if not compared_tables.limit(1).collect().height == 0:
            self.__compared_tables = compared_tables
            valid_tables_df = self.__compared_tables.select(
                ["rivers_str_answer"]
            ).collect()
            valid_tables_str = pl.Series(valid_tables_df).to_list()
            self.__valid_tables = [self.__rivers_dict[r] for r in valid_tables_str]
        else:
            raise ValueError(
                f"No rivers match colors={table_colors!r} for guess={guess_str!r}."
            )
        return self.__valid_tables

    def solve(self) -> list[list[Card]]:
        """Find all possible table runouts that maintain the expected hand rankings.

        Searches exhaustively through all possible flop/turn/river combinations
        to find tables that match the expected rankings at each phase. This is
        the primary method to call after initializing the Solver.

        Returns:
            list: List of valid tables (list[Card] with 5 cards each).

        Examples:
            >>> solver = Solver(p1hole, p2hole, p3hole, [2,1,3], [1,2,3], [1,2,3])
            >>> valid_tables = solver.solve()
            >>> len(valid_tables)
            412
        """
        flops = self.__possible_flops()
        turns = self.__possible_turns(flops)
        river_results = list(self.__possible_rivers(turns))

        # Extract just the tables (drop the cards_used metadata)
        self.__valid_tables = [table for table, _ in river_results]

        return self.__valid_tables

    @staticmethod
    def __player_hand_place(hand_ranks: list[int]) -> list[int]:
        """Convert list of player hands ordered by hand strength to a list of places for each player.

        Args:
            hand_ranks (list): A list of player hand ranks ordered by hand strength.

        Returns:
            list: A list where the index represents the player (0=P1, 1=P2, 2=P3) and the value represents their place (1=best, 2=second, 3=third).

        Example:
            >>> hand_ranks = [3, 1, 2]  # P2 has best hand, P1 second, P3 third
            >>> Solver.__player_hand_place(hand_ranks)
            [2, 3, 1]
        """
        enum_rankings = [
            (index, player) for index, player in enumerate(hand_ranks, start=1)
        ]
        enum_rankings.sort(key=lambda x: x[1])  # Sort by player number
        return [place for place, _ in enum_rankings]

    def print_game(self, table: list[Card]) -> None:
        """Print a formatted game state display with hand rankings and table cards.

        Shows player hole cards, hand strengths at each phase (flop/turn/river),
        and the current table being evaluated. Uses colored output to highlight
        rankings and cards.

        Args:
            table (list): The table to display (list of 5 Card objects).
            is_win (bool, optional): Whether this is the final winning guess. Defaults to False.

        Raises:
            ValueError: If solve() hasn't been called, table is invalid, or not in valid_tables.

        Examples:
            >>> solver.solve()
            >>> best_guess = solver.get_maxh_table()
            >>> solver.print_game(best_guess)
            Pokle Solver Results
                      P1   P2   P3
                     ---  ---  ---
                     ...
        """
        if not self.__valid_tables:
            raise ValueError("No possible rivers calculated. Please run solve() first.")
        if not isinstance(table, list) or len(table) != RIVER_SIZE:
            raise ValueError(f"Table must be a list of {RIVER_SIZE} Card objects.")

        hand_rank_symbols = {
            HAND_RANK_HIGH_CARD: "HC",
            HAND_RANK_PAIR: "1P",
            HAND_RANK_TWO_PAIR: "2P",
            HAND_RANK_THREE_KIND: "3K",
            HAND_RANK_STRAIGHT: "St",
            HAND_RANK_FLUSH: "Fl",
            HAND_RANK_FULL_HOUSE: "FH",
            HAND_RANK_FOUR_KIND: "4K",
            HAND_RANK_STRAIGHT_FLUSH: "SF",
        }

        # Format hole cards
        p1_0 = self.hole_cards["P1"][0].pstr().ljust(3)
        p2_0 = self.hole_cards["P2"][0].pstr().ljust(3)
        p3_0 = self.hole_cards["P3"][0].pstr().ljust(3)
        p1_1 = self.hole_cards["P1"][1].pstr().ljust(3)
        p2_1 = self.hole_cards["P2"][1].pstr().ljust(3)
        p3_1 = self.hole_cards["P3"][1].pstr().ljust(3)

        # Calculate hand ranks for flop
        flop_table = table[:FLOP_SIZE]
        p1_flop = (
            hand_rank_symbols[
                Solver.__rank_hand(flop_table, self.hole_cards["P1"]).rank
            ]
            + "\033[0m"
        )
        p2_flop = (
            hand_rank_symbols[
                Solver.__rank_hand(flop_table, self.hole_cards["P2"]).rank
            ]
            + "\033[0m"
        )
        p3_flop = (
            hand_rank_symbols[
                Solver.__rank_hand(flop_table, self.hole_cards["P3"]).rank
            ]
            + "\033[0m"
        )

        # Calculate hand ranks for turn
        turn_table = table[:TURN_SIZE]
        p1_turn = (
            hand_rank_symbols[
                Solver.__rank_hand(turn_table, self.hole_cards["P1"]).rank
            ]
            + "\033[0m"
        )
        p2_turn = (
            hand_rank_symbols[
                Solver.__rank_hand(turn_table, self.hole_cards["P2"]).rank
            ]
            + "\033[0m"
        )
        p3_turn = (
            hand_rank_symbols[
                Solver.__rank_hand(turn_table, self.hole_cards["P3"]).rank
            ]
            + "\033[0m"
        )

        # Calculate hand ranks for river (full table)
        p1_river = (
            hand_rank_symbols[Solver.__rank_hand(table, self.hole_cards["P1"]).rank]
            + "\033[0m"
        )
        p2_river = (
            hand_rank_symbols[Solver.__rank_hand(table, self.hole_cards["P2"]).rank]
            + "\033[0m"
        )
        p3_river = (
            hand_rank_symbols[Solver.__rank_hand(table, self.hole_cards["P3"]).rank]
            + "\033[0m"
        )

        # Format table cards for display
        flop_places = Solver.__player_hand_place(self.flop_hand_ranks)
        turn_places = Solver.__player_hand_place(self.turn_hand_ranks)
        river_places = Solver.__player_hand_place(self.river_hand_ranks)
        bg_colors = {
            1: "\033[48;2;255;215;0m",
            2: "\033[48;2;192;192;192m",
            3: "\033[48;2;205;127;50m",
        }

        print("Pokle Solver Results")
        print("              P1   P2   P3")
        print("             ---  ---  ---")
        print(f"             {p1_0}  {p2_0}  {p3_0}")
        print(f"             {p1_1}  {p2_1}  {p3_1}")
        print("      ------ ---  ---  ---")
        print(
            f"       flop:  {bg_colors[flop_places[0]]}{p1_flop}   {bg_colors[flop_places[1]]}{p2_flop}   {bg_colors[flop_places[2]]}{p3_flop}"
        )
        print(
            f"       turn:  {bg_colors[turn_places[0]]}{p1_turn}   {bg_colors[turn_places[1]]}{p2_turn}   {bg_colors[turn_places[2]]}{p3_turn}"
        )
        print(
            f"      river:  {bg_colors[river_places[0]]}{p1_river}   {bg_colors[river_places[1]]}{p2_river}   {bg_colors[river_places[2]]}{p3_river}"
        )

        if self.__used_tables and self.__current_colors:
            self.__used_tables[-1] = [
                ColorCard(card.rank, card.suit, color) if card is not None else None
                for card, color in zip(self.__used_tables[-1], self.__current_colors)
            ]
        congratulate_user = ""
        if (
            not all(color == "g" for color in self.__current_colors)
            or not self.__used_tables
        ):
            self.__used_tables.append(table)
        else:
            congratulate_user = f"Solved in {len(self.__used_tables)} Guesses! \n"

        print("|-----flop----|-turn|river|")
        for t in self.__used_tables:
            c_flop_cards = [card.pstr().ljust(3) for card in t[:FLOP_SIZE]]
            c_turn_card = t[FLOP_SIZE].pstr().ljust(3)
            c_river_card = t[TURN_SIZE].pstr().ljust(3)
            print(
                f"| {c_flop_cards[0]} {c_flop_cards[1]} {c_flop_cards[2]} | {c_turn_card} | {c_river_card} |"
            )
        print(congratulate_user)
