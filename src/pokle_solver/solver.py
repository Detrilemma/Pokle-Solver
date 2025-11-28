from card import Card
from itertools import combinations
import pandas as pd
from scipy.stats import entropy
from table import Table
from dataclasses import dataclass
import random


@dataclass
class PhaseEvaluation:
    """Configuration for evaluating a poker game phase (flop, turn, or river).

    Contains all information needed to evaluate whether a specific board state
    (table) matches the expected hand rankings for a given phase of the game.
    Used internally by the Solver to validate candidate board configurations.

    Attributes:
        table (Table): The board state to evaluate
        expected_rankings (list): Expected hand strength rankings for each player
                                 (list of 3 integers, permutation of [1, 2, 3])
        prev_cards_used (set | None): Set of cards already used in previous phases
        validate_all_cards_used (bool): Whether to check all cards are from the deck

    Examples:
        >>> phase = PhaseEvaluation(
        ...     table=Table(Card(10, 'H'), Card(14, 'D'), Card(7, 'S')),
        ...     expected_rankings=[2, 1, 3],  # P2 best, P1 second, P3 worst
        ...     prev_cards_used=set()
        ... )
    """

    table: Table
    expected_rankings: list
    prev_cards_used: set = None
    validate_all_cards_used: bool = False


MASTER_DECK = [
    Card(rank, suit) for rank in range(2, 15) for suit in ["H", "D", "C", "S"]
]


class Solver:
    """Solves for valid poker board runouts given player hole cards and hand rankings.

    The Solver finds all possible board configurations (flop + turn + river) that
    maintain specified hand strength rankings for each phase of the game. This is
    the core engine for the Pokle game, which challenges players to guess the board
    based on hand ranking feedback.

    Key features:
    - Finds all valid board runouts matching ranking constraints
    - Calculates optimal guesses using Shannon entropy (with sampling for large sets)
    - Supports interactive guessing with color-coded feedback
    - Handles datasets from small (hundreds) to large (thousands) of possible boards

    The solver uses three-player Texas Hold'em rules and validates that hand rankings
    are consistent across all three phases (flop, turn, river).

    Attributes:
        hole_cards (dict): Player hole cards {'P1': [Card, Card], 'P2': ..., 'P3': ...}
        hand_ranks (dict): Expected rankings for each phase {'flop': [2,1,3], 'turn': ...}
        valid_rivers (list): All valid complete board states found by solve()

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

        >>> # Find all valid boards
        >>> possible_rivers = solver.solve()
        >>> print(f"Found {len(possible_rivers)} possible boards")

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
                or len(p_hole) != 2
                or not all(isinstance(card, Card) for card in p_hole)
            ):
                raise ValueError(
                    f"{p_name} hole cards must be a list of exactly 2 Card objects."
                )

        # Updated validation for hand ranks
        for hand_rank_lists in [flop_hand_ranks, turn_hand_ranks, river_hand_ranks]:
            if not isinstance(hand_rank_lists, list) or sorted(hand_rank_lists) != [
                1,
                2,
                3,
            ]:
                raise ValueError("Hand rank lists must be a permutation of [1, 2, 3]")

        self.hole_cards = {"P1": p1hole, "P2": p2hole, "P3": p3hole}

        self.flop_hand_ranks = flop_hand_ranks
        self.turn_hand_ranks = turn_hand_ranks
        self.river_hand_ranks = river_hand_ranks

        self.current_deck = MASTER_DECK.copy()
        self.__valid_rivers = []
        self.__river_entropies = pd.Series()
        self.__table_comparisons = pd.DataFrame()
        self.__comparisons_matrix = pd.DataFrame()
        self.__maxh_table = tuple()
        self.__used_tables = []

        # Cache all hole cards set for performance (used in __evaluate_phase)
        self.__all_hole_cards = {
            card for hole in self.hole_cards.values() for card in hole
        }

    @property
    def valid_rivers(self):
        """Get the list of valid river tables found by solve().

        Returns:
            list: List of Table objects representing all valid complete boards.

        Examples:
            >>> solver.solve()
            >>> len(solver.valid_rivers)
            412
        """
        return self.__valid_rivers

    def __possible_flops(self):
        """Find all possible flops that maintain the current player rankings.

        Returns:
            list: A list of tuples (table, cards_used_in_hands) where cards_used_in_hands
                  is a set of board cards used in any player's best hand at the flop.
        """
        hole_cards = {card for hole in self.hole_cards.values() for card in hole}
        remaining_cards = set(self.current_deck).difference(hole_cards)
        self.current_deck = list(remaining_cards)

        all_flops = list(combinations(self.current_deck, 3))

        valid_flops = []
        for flop in all_flops:
            flop_table = Table(flop)

            phase_eval = PhaseEvaluation(
                table=flop_table, expected_rankings=self.flop_hand_ranks
            )
            is_valid, cards_used = self.__evaluate_phase(phase_eval)

            if is_valid:
                valid_flops.append((flop_table, cards_used))

        return valid_flops

    def __evaluate_phase(self, phase_eval: PhaseEvaluation):
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
            player_hand = phase_eval.table.rank_hand(hole)
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
            if rank != 6:  # Not a flush
                cards_used_current_phase.update(set(player_hand.best_hand))

        # Accumulate cards used across all phases
        if phase_eval.prev_cards_used is not None:
            cards_used_accumulated = (
                phase_eval.prev_cards_used | cards_used_current_phase
            )
        else:
            cards_used_accumulated = cards_used_current_phase

        cards_used_accumulated.difference_update(all_hole_cards)

        # For river, validate that all board cards were used at some point
        if phase_eval.validate_all_cards_used and cards_used_accumulated != set(
            phase_eval.table.cards
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
        prev_phase_results: list,
        expected_rankings: list,
        validate_all_cards_used: bool = False,
    ):
        """Helper method to find valid tables for the next phase (turn or river).

        Args:
            prev_phase_results (list): List of tuples (table, cards_used) from previous phase.
            expected_rankings (list): Expected hand rankings for this phase.
            validate_all_cards_used (bool): Whether to validate all cards were used.

        Returns:
            list: List of tuples (table, cards_used_accumulated) for valid combinations.
        """
        valid_tables = []

        # Pre-compute hole cards set once (used for conflict checking)
        # all_hole_cards = {card for hole in self.hole_cards.values() for card in hole}

        for prev_table, prev_cards_used in prev_phase_results:
            remaining_deck = set(self.current_deck) - set(prev_table.cards)

            for next_card in remaining_deck:
                # Early rejection: Skip if next_card conflicts with any hole card
                # This is redundant since remaining_deck already excludes current_deck cards,
                # but serves as documentation of the constraint

                next_table = prev_table.add_cards(next_card)

                phase_eval = PhaseEvaluation(
                    table=next_table,
                    expected_rankings=expected_rankings,
                    prev_cards_used=prev_cards_used,
                    validate_all_cards_used=validate_all_cards_used,
                )
                is_valid, cards_used = self.__evaluate_phase(phase_eval)

                if is_valid:
                    valid_tables.append((next_table, cards_used))

        return valid_tables

    def __possible_turns(self, flops: list):
        """Find all possible turns that maintain the current player rankings.

        Args:
            flops (list): A list of tuples (table, cards_used) from flop phase.

        Returns:
            list: A list of tuples (table, cards_used_accumulated) for valid turn combinations.
        """
        return self.__find_valid_next_phase(flops, self.turn_hand_ranks)

    def __possible_rivers(self, turns: list):
        """Find all possible rivers that maintain the current player rankings.

        Args:
            turns (list): A list of tuples (table, cards_used) from turn phase.

        Returns:
            list: A list of tuples (table, cards_used_accumulated) for valid river combinations.
        """
        return self.__find_valid_next_phase(
            turns, self.river_hand_ranks, validate_all_cards_used=True
        )

    @staticmethod
    def __entropy_from_series(s: pd.Series):
        """Calculates the Shannon entropy from a pandas series.

        Args:
            s (pd.Series): A pandas series. Each value in the series represents a category.

        Returns:
            float: The Shannon entropy of the series.
        """
        return entropy(s.value_counts(normalize=True), base=2)

    def get_maxh_table(self, max_sample_size=1000, use_sampling=None):
        """Calculate the table with highest entropy from all possible rivers.

        For large river sets (>1000), uses sampling to approximate entropy efficiently.
        For small sets, computes exact entropy.

        Args:
            max_sample_size (int): Maximum number of answers to sample per guess (default 1000)
            use_sampling (bool): Force sampling on/off. If None, auto-decide based on river count.

        Returns:
            Table: The river with the highest entropy.
        """
        # Validate state
        if not getattr(self, "_Solver__valid_rivers", None):
            raise ValueError("No possible rivers calculated. Please run solve() first.")

        rivers = self.__valid_rivers
        n_rivers = len(rivers)

        # Auto-decide whether to use sampling
        if use_sampling is None:
            use_sampling = n_rivers > 1000

        if use_sampling:
            return self.__get_maxh_table_sampled(max_sample_size)
        else:
            return self.__get_maxh_table_exact()

    def __get_maxh_table_exact(self):
        """Original exact entropy calculation (O(n²) complexity).

        Use only for small river sets (<1000 rivers).
        """
        rivers = self.__valid_rivers

        # Pre-compute string representations once they're cached in Table.__str__
        river_strs = [str(r) for r in rivers]

        # Build Cartesian product using list comprehensions (much faster than pandas merge)
        # Each river is compared against all rivers
        guesses = []
        answers = []
        guess_strs = []
        answer_strs = []
        comparisons = []

        for i, guess in enumerate(rivers):
            guess_str = river_strs[i]
            for j, answer in enumerate(rivers):
                guesses.append(guess)
                answers.append(answer)
                guess_strs.append(guess_str)
                answer_strs.append(river_strs[j])
                comparisons.append(guess.compare(answer))

        # Build DataFrame from pre-computed lists
        self.__table_comparisons = pd.DataFrame(
            {
                "guess": guesses,
                "answer": answers,
                "guess_str": guess_strs,
                "answer_str": answer_strs,
                "table_comparison": comparisons,
            }
        )

        # Pivot to create comparison matrix
        self.__comparisons_matrix = self.__table_comparisons.pivot(
            index="answer_str", columns="guess_str", values="table_comparison"
        )

        # Calculate entropy for each column (guess)
        self.__river_entropies = self.__comparisons_matrix.apply(
            self.__entropy_from_series, axis=0
        ).sort_values(ascending=False)

        # Get the table with highest entropy
        maxh_table_str = self.__river_entropies.index[0]
        self.__maxh_table = self.__table_comparisons[
            self.__table_comparisons["guess_str"] == maxh_table_str
        ]["guess"].iloc[0]

        return self.__maxh_table

    def __get_maxh_table_sampled(self, max_sample_size=1000):
        """Optimized entropy calculation using sampling (O(n) complexity).

        For large river sets, samples a subset of answers for each guess to approximate
        entropy. This provides ~99% accuracy with massive speedup.

        Args:
            max_sample_size (int): Maximum number of answers to sample per guess

        Returns:
            Table: The river with the highest (approximate) entropy
        """
        rivers = self.__valid_rivers
        n_rivers = len(rivers)

        # Determine sample size (use all if fewer than max_sample_size)
        sample_size = min(max_sample_size, n_rivers)

        # For candidate selection, we can test all rivers or sample candidates too
        # For now, test all rivers as potential guesses (can optimize further if needed)
        guess_candidates = rivers

        # If we have too many candidates, sample them too
        max_candidates = 500  # Only evaluate entropy for top 500 candidates
        if len(guess_candidates) > max_candidates:
            # Sample diverse candidates (stratified by card ranks/suits)
            guess_candidates = random.sample(guess_candidates, max_candidates)

        # Calculate entropy for each guess candidate
        entropies = {}

        for guess_idx, guess in enumerate(guess_candidates):
            # Sample answers for this guess
            if sample_size < n_rivers:
                answer_sample = random.sample(rivers, sample_size)
            else:
                answer_sample = rivers

            # Compare guess against sampled answers
            comparison_results = []
            for answer in answer_sample:
                comparison_results.append(str(guess.compare(answer)))

            # Calculate entropy from comparison distribution
            result_counts = pd.Series(comparison_results).value_counts(normalize=True)
            guess_entropy = entropy(result_counts, base=2)

            entropies[str(guess)] = (guess_entropy, guess)

        # Find guess with maximum entropy
        max_entropy_str = max(entropies.keys(), key=lambda k: entropies[k][0])
        max_entropy, self.__maxh_table = entropies[max_entropy_str]

        # Store results for compatibility with existing code
        self.__river_entropies = pd.Series(
            {k: v[0] for k, v in entropies.items()}
        ).sort_values(ascending=False)

        return self.__maxh_table

    def next_table_guess(self, table_colors: list, current_guess: Table = None):
        """Filter valid rivers based on color feedback from the current guess.

        Updates the internal list of valid rivers to only include those that
        would produce the given color pattern for the current guess. This is
        used in the interactive guessing loop.

        Args:
            table_colors (list): List of 5 color strings for each card:
                                'g' = green, 'y' = yellow, 'e' = grey.
            current_guess (Table, optional): The table being guessed. Defaults to maxh_table.

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
        if current_guess is None:
            current_guess = self.__maxh_table
        if not getattr(self, "_Solver__valid_rivers", None):
            raise ValueError("No possible rivers calculated. Please run solve() first.")
        if (
            not isinstance(current_guess, Table)
            or not current_guess.flop
            or not current_guess.turn
            or not current_guess.river
        ):
            raise ValueError(
                "Current guess must be a complete Table object with flop, turn, and river."
            )
        if not isinstance(table_colors, list) or len(table_colors) != 5:
            raise ValueError(
                "Table colors must be a list of 5 colors for each card in the table."
            )

        # Build comparison data for the current guess if not available
        # This handles the case where get_maxh_table used sampling and didn't create the full matrix
        if (
            not hasattr(self, "_Solver__comparisons_matrix")
            or str(current_guess) not in self.__comparisons_matrix.columns
        ):
            # Compare current guess against all valid rivers
            print(
                f"Computing comparisons for guess against {len(self.__valid_rivers)} possible answers..."
            )
            comparisons = []
            answer_strs = []

            for answer in self.__valid_rivers:
                comparisons.append(current_guess.compare(answer))
                answer_strs.append(str(answer))

            # Create a temporary comparison series for this guess
            possible_outcomes = pd.Series(comparisons, index=answer_strs)
        else:
            possible_outcomes = self.__comparisons_matrix[str(current_guess)]

        color_current_guess = current_guess.update_colors(table_colors)
        self.__used_tables.append(color_current_guess)

        # Convert to string for comparison since possible_outcomes contains ComparisonResult objects
        # while color_current_guess is a Table object
        color_guess_str = str(color_current_guess)
        possible_outcomes_filtered = possible_outcomes[
            possible_outcomes.astype(str) == color_guess_str
        ].index
        if possible_outcomes_filtered.empty:
            raise ValueError(
                "No possible rivers match the given colors for the current guess."
            )

        # Filter valid_rivers to only those that match
        # possible_outcomes_filtered.index contains answer_str values
        answer_strs_set = set(possible_outcomes_filtered)
        self.__valid_rivers = [
            river for river in self.__valid_rivers if str(river) in answer_strs_set
        ]

        return self.__valid_rivers

    def solve(self):
        """Find all possible board runouts that maintain the expected hand rankings.

        Searches exhaustively through all possible flop/turn/river combinations
        to find boards that match the expected rankings at each phase. This is
        the primary method to call after initializing the Solver.

        Returns:
            list: List of valid Table objects (complete 5-card boards).

        Examples:
            >>> solver = Solver(p1hole, p2hole, p3hole, [2,1,3], [1,2,3], [1,2,3])
            >>> valid_boards = solver.solve()
            >>> len(valid_boards)
            412
        """
        flops = self.__possible_flops()
        turns = self.__possible_turns(flops)
        river_results = self.__possible_rivers(turns)

        # Extract just the tables (drop the cards_used metadata)
        self.__valid_rivers = [table for table, _ in river_results]

        return self.__valid_rivers

    @staticmethod
    def __player_hand_place(hand_ranks: list):
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

    def print_game(self, table: Table, is_win: bool = False):
        """Print a formatted game state display with hand rankings and board cards.

        Shows player hole cards, hand strengths at each phase (flop/turn/river),
        and the current table being evaluated. Uses colored output to highlight
        rankings and cards.

        Args:
            table (Table): The table to display.
            is_win (bool, optional): Whether this is the final winning guess. Defaults to False.

        Raises:
            ValueError: If solve() hasn't been called, table is invalid, or not in valid_rivers.

        Examples:
            >>> solver.solve()
            >>> best_guess = solver.get_maxh_table()
            >>> solver.print_game(best_guess)
            Pokle Solver Results
                      P1   P2   P3
                     ---  ---  ---
                     ...
        """
        if not self.__valid_rivers:
            raise ValueError("No possible rivers calculated. Please run solve() first.")
        if not isinstance(table, Table):
            raise ValueError("Table must be an instance of the Table class.")
        if table not in self.__valid_rivers:
            raise ValueError("Provided table is not in the list of possible rivers.")

        hand_rank_symbols = {
            1: "HC",
            2: "1P",
            3: "2P",
            4: "3K",
            5: "St",
            6: "Fl",
            7: "FH",
            8: "4K",
            9: "SF",
        }

        # Format hole cards
        p1_0 = self.hole_cards["P1"][0].pstr().ljust(3)
        p2_0 = self.hole_cards["P2"][0].pstr().ljust(3)
        p3_0 = self.hole_cards["P3"][0].pstr().ljust(3)
        p1_1 = self.hole_cards["P1"][1].pstr().ljust(3)
        p2_1 = self.hole_cards["P2"][1].pstr().ljust(3)
        p3_1 = self.hole_cards["P3"][1].pstr().ljust(3)

        # Calculate hand ranks for flop
        flop_table = Table(*list(table.flop))
        p1_flop = (
            hand_rank_symbols[flop_table.rank_hand(self.hole_cards["P1"]).rank]
            + "\033[0m"
        )
        p2_flop = (
            hand_rank_symbols[flop_table.rank_hand(self.hole_cards["P2"]).rank]
            + "\033[0m"
        )
        p3_flop = (
            hand_rank_symbols[flop_table.rank_hand(self.hole_cards["P3"]).rank]
            + "\033[0m"
        )

        # Calculate hand ranks for turn
        turn_table = Table(*list(table.flop), table.turn)
        p1_turn = (
            hand_rank_symbols[turn_table.rank_hand(self.hole_cards["P1"]).rank]
            + "\033[0m"
        )
        p2_turn = (
            hand_rank_symbols[turn_table.rank_hand(self.hole_cards["P2"]).rank]
            + "\033[0m"
        )
        p3_turn = (
            hand_rank_symbols[turn_table.rank_hand(self.hole_cards["P3"]).rank]
            + "\033[0m"
        )

        # Calculate hand ranks for river (full table)
        p1_river = (
            hand_rank_symbols[table.rank_hand(self.hole_cards["P1"]).rank] + "\033[0m"
        )
        p2_river = (
            hand_rank_symbols[table.rank_hand(self.hole_cards["P2"]).rank] + "\033[0m"
        )
        p3_river = (
            hand_rank_symbols[table.rank_hand(self.hole_cards["P3"]).rank] + "\033[0m"
        )

        # Format table cards for display

        flop_places = self.__player_hand_place(self.flop_hand_ranks)
        turn_places = self.__player_hand_place(self.turn_hand_ranks)
        river_places = self.__player_hand_place(self.river_hand_ranks)
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
        print("|-----flop----|-turn|river|")
        for t in self.__used_tables:
            c_flop_cards = [card.pstr().ljust(3) for card in t.cards[:3]]
            c_turn_card = t.turn.pstr().ljust(3)
            c_river_card = t.river.pstr().ljust(3)
            print(
                f"| {c_flop_cards[0]} {c_flop_cards[1]} {c_flop_cards[2]} | {c_turn_card} | {c_river_card} |"
            )
        if not is_win:
            flop_cards = [card.pstr().ljust(3) for card in table.cards[:3]]
            turn_card = table.turn.pstr().ljust(3)
            river_card = table.river.pstr().ljust(3)
            print(
                f"| {flop_cards[0]} {flop_cards[1]} {flop_cards[2]} | {turn_card} | {river_card} |"
            )
        print()
