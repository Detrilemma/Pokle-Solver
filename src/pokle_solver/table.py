from __future__ import annotations
from card import Card, ColorCard
from dataclasses import dataclass
from functools import cache


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

    Examples:
        >>> HandRanking(rank=2, tie_breakers=(10, 14, 13, 12), best_hand=(...))  # Pair of 10s
        >>> HandRanking(rank=9, tie_breakers=(14,), best_hand=(...))  # Royal flush
    """

    rank: int  # Numerical rank (1=high card, 2=pair, ..., 9=straight flush)
    tie_breakers: tuple  # Tuple of ranks for tie-breaking
    best_hand: tuple  # Tuple of Card objects in the best 5-card hand


class ComparisonResult:
    """Lightweight result of comparing two Tables with color-coded feedback.

    Represents the result of comparing a guess Table to an answer Table,
    showing which cards match (green), partially match (yellow), or don't
    match (grey). This is optimized for performance by avoiding the overhead
    of creating a full Table object.

    ComparisonResult is immutable and uses __slots__ for memory efficiency.

    Attributes:
        cards (tuple): Tuple of 5 ColorCard objects representing the comparison
                      result for each card in the table (flop + turn + river)

    Examples:
        >>> # Green = exact match, Yellow = partial match, Grey = no match
        >>> result = ComparisonResult([ColorCard(10, 'H', 'g'), ...])
        >>> str(result)  # "10H_g KD_y AS_e 7C_e 4S_y"
    """

    __slots__ = ("_cards", "_str_cache", "_hash_cache", "_canonical")

    def __init__(self, cards: list):
        self._cards = tuple(cards)
        self._str_cache = None
        self._hash_cache = None
        # Pre-compute canonical form (sorted flop + remaining) once
        self._canonical = tuple(sorted(self._cards[:3])) + self._cards[3:]

    @property
    def cards(self):
        return self._cards

    def __str__(self):
        if self._str_cache is None:
            self._str_cache = " ".join(str(card) for card in self._canonical)
        return self._str_cache

    def __repr__(self):
        return f"ComparisonResult({', '.join(repr(card) for card in self._canonical)})"

    def __hash__(self):
        if self._hash_cache is None:
            self._hash_cache = hash(self._canonical)
        return self._hash_cache

    def __eq__(self, other):
        if isinstance(other, ComparisonResult):
            return self._canonical == other._canonical
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, ComparisonResult):
            return self._canonical < other._canonical
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, ComparisonResult):
            return self._canonical <= other._canonical
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, ComparisonResult):
            return self._canonical > other._canonical
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, ComparisonResult):
            return self._canonical >= other._canonical
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, ComparisonResult):
            return self._canonical != other._canonical
        return NotImplemented


class Table:
    """Represents a poker board state (flop, turn, and/or river cards).

    A Table represents the community cards in a poker game, consisting of:
    - Flop: First 3 cards (required)
    - Turn: 4th card (optional)
    - River: 5th card (optional)

    Tables are immutable and optimized for performance using __slots__.
    They support comparison operations to generate color-coded feedback for
    the Pokle guessing game, and can evaluate poker hand rankings when combined
    with player hole cards.

    Attributes:
        cards (tuple): All cards in the table (3-5 cards)
        flop (frozenset): The first 3 cards (immutable set)
        turn (Card | None): The 4th card, or None if not set
        river (Card | None): The 5th card, or None if not set

    Examples:
        >>> # Create a table with just the flop
        >>> table = Table(Card(10, 'H'), Card(14, 'D'), Card(7, 'S'))

        >>> # Create a complete table (flop + turn + river)
        >>> table = Table(Card(10, 'H'), Card(14, 'D'), Card(7, 'S'),
        ...               Card(13, 'C'), Card(4, 'H'))

        >>> # Add cards to an existing table
        >>> new_table = table.add_cards(Card(13, 'C'))

        >>> # Compare two tables (for Pokle game)
        >>> result = guess_table.compare(answer_table)  # Returns ComparisonResult
    """

    __slots__ = ("_cards", "_flop", "_turn", "_river", "_str_cache")

    def __init__(self, *cards: Card, _skip_validation: bool = False):
        # If a single tuple/list is passed, unpack it
        if len(cards) == 1 and isinstance(cards[0], (tuple, list)):
            cards_list = cards[0] if isinstance(cards[0], list) else list(cards[0])
        else:
            # Multiple positional arguments
            cards_list = list(cards)

        # Skip validation when called from trusted internal methods
        if not _skip_validation:
            # Validate all items are Card objects
            if not all(isinstance(card, Card) for card in cards_list):
                raise ValueError("All items must be Card objects")
            if len(cards_list) < 3 or len(cards_list) > 5:
                raise ValueError("Table must have between 3 and 5 cards")

        self._cards = tuple(sorted(cards_list[:3]) + list(cards_list[3:]))  # Ensure flop is ordered
        # self._cards = tuple(cards_list)
        self._flop = frozenset(self._cards[:3])
        self._turn = self._cards[3] if len(self._cards) >= 4 else None
        self._river = self._cards[4] if len(self._cards) == 5 else None

        # Cache string representation for performance (called millions of times)
        self._str_cache = None

    def __repr__(self):
        return "Table(" + ", ".join(repr(card) for card in self.cards) + ")"

    def __str__(self):
        if self._str_cache is None:
            self._str_cache = " ".join(str(card) for card in self.cards)
        return self._str_cache

    def pstr(self):
        """Return a pretty-printed colored string of all cards.

        Returns:
            str: ANSI colored string representation.

        Examples:
            >>> table = Table(Card(10, 'H'), Card(14, 'D'), Card(7, 'S'))
            >>> table.pstr()  # Returns colored output
        """
        return " ".join(card.pstr() for card in self.cards)

    def __eq__(self, value):
        if not isinstance(value, Table):
            return NotImplemented
        is_flop_eq = self.flop == value.flop
        is_turn_eq = self.turn == value.turn
        is_river_eq = self.river == value.river
        return (is_flop_eq and is_turn_eq and is_river_eq)

    def __ne__(self, value):
        if not isinstance(value, Table):
            return NotImplemented
        is_flop_eq = self.flop == value.flop
        is_turn_eq = self.turn == value.turn
        is_river_eq = self.river == value.river
        return not (is_flop_eq and is_turn_eq and is_river_eq)

    @property
    def cards(self):
        return self._cards

    @property
    def flop(self):
        return self._flop

    @property
    def turn(self):
        return self._turn

    @property
    def river(self):
        return self._river

    def add_cards(self, *cards):
        """Add one or more cards to the table and return a new Table.

        Args:
            *cards: Card objects or a single list/tuple of Cards.

        Returns:
            Table: A new Table instance with the added cards.

        Raises:
            ValueError: If cards are not Card objects or total exceeds 5.

        Examples:
            >>> table = Table(Card(10, 'H'), Card(14, 'D'), Card(7, 'S'))
            >>> new_table = table.add_cards(Card(13, 'C'))
            >>> len(new_table.cards)
            4
        """
        # Handle both single card and iterable
        if len(cards) == 1 and isinstance(cards[0], (tuple, list)):
            new_cards = cards[0]
        else:
            new_cards = cards

        # Validate
        if not all(isinstance(card, Card) for card in new_cards):
            raise ValueError("All items must be Card objects")

        total_cards = self.cards + tuple(new_cards)
        if len(total_cards) > 5:
            raise ValueError("Table cannot have more than 5 cards")

        # Skip validation in __init__ since we already validated
        return Table(total_cards, _skip_validation=True)

    @staticmethod
    @cache
    def __compare_flop(self_flop: list, other_flop: frozenset) -> list:
        """Compare two flops and return a list of ColorCards indicating matches.

        Args:
            self_flop (list): List of Card objects in this Table's flop (ordered, first 3 cards).
            other_flop (frozenset): Frozenset of Card objects in the other Table's flop.

        Returns:
            list: List of 3 ColorCard objects with colors indicating matches:
                  'g' = exact match, 'y' = partial match (rank or suit), 'e' = no match.

        Examples:
            >>> flop1 = [Card(10, 'H'), Card(14, 'D'), Card(7, 'S')]
            >>> flop2 = frozenset([Card(10, 'H'), Card(13, 'D'), Card(8, 'S')])
            >>> result = Table.__compare_flop(tuple(flop1), flop2)
            >>> result[0].color  # 10H exact match
            'g'
            >>> result[1].color  # AD partial match (D suit)
            'y'
        """
        # Convert tuple to frozenset for set operations
        self_flop_set = frozenset(self_flop)
        green_flop_cards = self_flop_set & other_flop

        # Build lookup sets for remaining (non-green) cards
        other_remaining = other_flop - green_flop_cards
        other_ranks = {card.rank for card in other_remaining}
        other_suits = {card.suit for card in other_remaining}
        color_cards = []
        # Iterate over tuple to maintain card order
        for card in self_flop:
            if card in green_flop_cards:
                color_cards.append(ColorCard(card.rank, card.suit, "g"))
            elif card.rank in other_ranks or card.suit in other_suits:
                color_cards.append(ColorCard(card.rank, card.suit, "y"))
            else:
                color_cards.append(ColorCard(card.rank, card.suit, "e"))

        return color_cards

    @staticmethod
    @cache
    def __compare_single_card(self_card: Card, other_card: Card) -> ColorCard:
        """Compare two single cards and return a ColorCard indicating the match.

        Args:
            self_card (Card): Card object in this Table.
            other_card (Card): Card object in the other Table.

        Returns:
            ColorCard: ColorCard with color indicating match:
                      'g' = exact match, 'y' = partial match (rank or suit), 'e' = no match.

        Examples:
            >>> result = Table.__compare_single_card(Card(13, 'C'), Card(13, 'C'))
            >>> result.color
            'g'
            >>> result = Table.__compare_single_card(Card(13, 'C'), Card(13, 'H'))
            >>> result.color
            'y'
        """
        s_rank, s_suit = self_card.rank, self_card.suit
        o_rank, o_suit = other_card.rank, other_card.suit

        if s_rank == o_rank and s_suit == o_suit:
            return ColorCard(s_rank, s_suit, "g")
        elif s_rank == o_rank or s_suit == o_suit:
            return ColorCard(s_rank, s_suit, "y")
        else:
            return ColorCard(s_rank, s_suit, "e")

    def compare(self, other: Table) -> ComparisonResult:
        """Compare this Table with another Table and return a ComparisonResult with ColorCards.

        Args:
            other (Table): The Table to compare against (usually the answer table).

        Returns:
            ComparisonResult: A lightweight object containing ColorCards where:
                             'g' (green) = exact match
                             'y' (yellow) = partial match (rank or suit matches)
                             'e' (grey) = no match

        Raises:
            ValueError: If other is not a Table or if tables have different lengths.

        Examples:
            >>> guess = Table(Card(10, 'H'), Card(14, 'D'), Card(7, 'S'))
            >>> answer = Table(Card(10, 'H'), Card(13, 'D'), Card(8, 'S'))
            >>> result = guess.compare(answer)
            >>> result.cards[0].color  # 10H is exact match
            'g'
            >>> result.cards[1].color  # AD has D suit match
            'y'
        """
        if not isinstance(other, Table):
            raise ValueError("other must be an instance of Table")
        if len(self.cards) != len(other.cards):
            raise ValueError(
                "Both tables must have the same number of cards to compare"
            )

        # Get a COPY of the cached list to avoid mutating the cache
        color_cards = list(self.__compare_flop(self.cards[:3], other.flop))

        if self.turn and other.turn:
            color_cards.append(self.__compare_single_card(self.turn, other.turn))

        if self.river and other.river:
            color_cards.append(self.__compare_single_card(self.river, other.river))

        return ComparisonResult(color_cards)

    def update_colors(self, colors: list[str]) -> Table:
        """Create a new Table with updated card colors.

        Args:
            colors (list[str]): List of color codes ('g', 'y', 'e') for each card.

        Returns:
            Table: New Table instance with ColorCards instead of Cards.

        Raises:
            ValueError: If colors length doesn't match cards or contains invalid colors.

        Examples:
            >>> table = Table(Card(10, 'H'), Card(14, 'D'), Card(7, 'S'))
            >>> colored = table.update_colors(['g', 'y', 'e'])
            >>> colored.cards[0]
            ColorCard(rank=10, suit='H', color='g')
        """
        if len(colors) != len(self.cards):
            raise ValueError(
                "Length of colors list must match number of cards in the table"
            )
        if not all(color in ["g", "y", "e"] for color in colors):
            raise ValueError("Colors must be one of 'g', 'y', or 'e'")

        updated_cards = [
            ColorCard(card.rank, card.suit, color)
            for card, color in zip(self.cards, colors)
        ]

        return Table(updated_cards)

    def rank_hand(self, hole: list) -> HandRanking:
        """Evaluate the best 5-card poker hand from hole cards and table cards.

        Args:
            hole (list): List of 2 Card objects (player's hole cards).

        Returns:
            HandRanking: Dataclass containing:
                - rank (int): Hand type (1=high card ... 9=straight flush)
                - tie_breakers (tuple): Ranks for breaking ties
                - best_hand (tuple): Best 5 Card objects

        Examples:
            >>> table = Table(Card(10, 'H'), Card(11, 'H'), Card(12, 'H'))
            >>> hole = [Card(13, 'H'), Card(14, 'H')]
            >>> ranking = table.rank_hand(hole)
            >>> ranking.rank
            9  # Straight flush
            >>> ranking.tie_breakers
            (14,)  # Ace-high
        """
        cards = hole + list(self.cards)

        # Count occurrences of each rank and group cards by suit in single pass
        # Use lists for rank_groups instead of defaultdict(list) to reduce overhead
        rank_groups = {}
        suit_groups = {}

        for card in cards:
            rank = card.rank
            suit = card.suit

            # Manually manage dict entries to avoid defaultdict overhead
            if rank in rank_groups:
                rank_groups[rank].append(card)
            else:
                rank_groups[rank] = [card]

            if suit in suit_groups:
                suit_groups[suit].append(card)
            else:
                suit_groups[suit] = [card]

        # Check for flush - avoid creating flush_cards list if not needed
        flush_cards = None
        for suit, suited_cards in suit_groups.items():
            suited_count = len(suited_cards)
            if suited_count >= 5:
                flush_cards = sorted(
                    suited_cards, key=lambda card: card.rank, reverse=True
                )
                break

        # Check for straight - pre-sort ranks once
        ranks = sorted(set(card.rank for card in cards), reverse=True)
        straight_high_card = None

        # Standard straight check
        ranks_len = len(ranks)
        for i in range(ranks_len - 4):
            if ranks[i] - ranks[i + 4] == 4:  # 5 consecutive ranks
                straight_high_card = ranks[i]
                break

        # Special case for A-5-4-3-2 (Ace low straight)
        if not straight_high_card:
            # Use a set for faster membership testing
            ranks_set = set(ranks)
            if (
                14 in ranks_set
                and 5 in ranks_set
                and 4 in ranks_set
                and 3 in ranks_set
                and 2 in ranks_set
            ):
                straight_high_card = 5

        # Check for straight flush
        if flush_cards and straight_high_card:
            flush_ranks = [c.rank for c in flush_cards]
            flush_ranks_set = set(flush_ranks)  # Use set for faster membership

            best_hand = [
                c
                for c in flush_cards
                if straight_high_card >= c.rank >= straight_high_card - 4
            ][:5]

            # Standard straight flush check
            if straight_high_card != 5:
                # Check if all 5 consecutive ranks are in flush
                has_straight_flush = True
                for r in range(straight_high_card - 4, straight_high_card + 1):
                    if r not in flush_ranks_set:
                        has_straight_flush = False
                        break

                if has_straight_flush:
                    return HandRanking(9, (straight_high_card,), tuple(best_hand))

            # A-5-4-3-2 straight flush
            elif (
                14 in flush_ranks_set
                and 5 in flush_ranks_set
                and 4 in flush_ranks_set
                and 3 in flush_ranks_set
                and 2 in flush_ranks_set
            ):
                return HandRanking(9, (5,), tuple(best_hand))

        # Pre-compute group sizes to avoid repeated len() calls
        three_ranks = []
        pair_ranks = []
        four_rank = None

        for rank, group in rank_groups.items():
            group_len = len(group)
            if group_len == 4:
                four_rank = rank
                break  # Found four of a kind, stop looking
            elif group_len == 3:
                three_ranks.append(rank)
            elif group_len == 2:
                pair_ranks.append(rank)

        # Check for four of a kind
        if four_rank is not None:
            four_of_a_kind = rank_groups[four_rank]
            return HandRanking(8, (four_rank,), tuple(four_of_a_kind))

        # Check for full house
        if (three_ranks and pair_ranks) or len(three_ranks) > 1:
            max_three = max(three_ranks)
            three_of_a_kind = rank_groups[max_three]

            if pair_ranks:
                max_pair_rank = max(pair_ranks)
                pair = rank_groups[max_pair_rank]
            else:
                min_three = min(three_ranks)
                second_three = rank_groups[min_three]
                pair = second_three[:2]
                max_pair_rank = pair[0].rank

            best_hand = three_of_a_kind + pair
            return HandRanking(7, (max_three, max_pair_rank), tuple(best_hand))

        # Check for flush
        if flush_cards:
            flush_card_hand = flush_cards[:5]
            flush_card_hand_ranks = tuple(c.rank for c in flush_card_hand)
            return HandRanking(6, flush_card_hand_ranks, tuple(flush_card_hand))

        # Check for straight
        if straight_high_card:
            if straight_high_card == 5:  # A-5-4-3-2
                best_hand = [c for c in cards if c.rank in (14, 5, 4, 3, 2)]
                # Sort to ensure proper order
                best_hand.sort(
                    key=lambda c: (1 if c.rank == 14 else c.rank), reverse=True
                )
            else:
                best_hand = sorted(
                    [
                        c
                        for c in cards
                        if straight_high_card >= c.rank >= straight_high_card - 4
                    ],
                    reverse=True,
                )
            return HandRanking(5, (straight_high_card,), tuple(best_hand[:5]))

        # Check for three of a kind
        if three_ranks:
            max_three = max(three_ranks)
            three_of_a_kind = rank_groups[max_three]
            remaining = sorted(set(cards) - set(three_of_a_kind), reverse=True)
            remaining_ranks = [c.rank for c in remaining[:2]]
            return HandRanking(
                4,
                tuple([max_three] + remaining_ranks),
                tuple(three_of_a_kind),
            )

        # Check for two pair
        pair_ranks_len = len(pair_ranks)
        if pair_ranks_len >= 2:
            pair_ranks.sort(reverse=True)
            two_pair = rank_groups[pair_ranks[0]] + rank_groups[pair_ranks[1]]
            remaining = sorted(set(cards) - set(two_pair), reverse=True)
            remaining_rank = remaining[0].rank if remaining else 0
            return HandRanking(
                3,
                tuple([pair_ranks[0], pair_ranks[1], remaining_rank]),
                tuple(two_pair),
            )

        # Check for one pair
        if pair_ranks:
            pair_rank = pair_ranks[0]
            pair = rank_groups[pair_rank]
            remaining = sorted(set(cards) - set(pair), reverse=True)
            remaining_ranks = [c.rank for c in remaining[:3]]
            return HandRanking(2, tuple([pair_rank] + remaining_ranks), tuple(pair))

        # High card
        best_hand = sorted(cards, reverse=True)[:5]
        best_hand_ranks = tuple(c.rank for c in best_hand)
        return HandRanking(
            1,
            best_hand_ranks,
            tuple([best_hand[0]]),
        )  # Return only the highest card for high card
