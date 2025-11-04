from __future__ import annotations
from card import *
import numpy as np
from collections import defaultdict


class Table:
    def __init__(self, *cards: Card):
        # If a single tuple/list is passed, unpack it
        if len(cards) == 1 and isinstance(cards[0], (tuple, list)):
            self._cards = tuple(cards[0])
        else:
            # Multiple positional arguments
            self._cards = tuple(cards)
        
        # Validate all items are Card objects
        if not all(isinstance(card, Card) for card in self._cards):
            raise ValueError("All items must be Card objects")
        if len(self._cards) < 3 or len(self._cards) > 5:
            raise ValueError("Table must have between 3 and 5 cards")

        self._flop = frozenset(self._cards[:3])
        self._turn = self._cards[3] if len(self._cards) >= 4 else None
        self._river = self._cards[4] if len(self._cards) == 5 else None

    def __repr__(self):
        return "Table(" + ", ".join(repr(card) for card in self.cards) + ")"
    
    def __str__(self):
        return " ".join(str(card) for card in self.cards)
    
    def pstr(self):
        return " ".join(card.pstr() for card in self.cards)
    
    def __eq__(self, value):
        if not isinstance(value, Table):
            return NotImplemented
        is_flop_eq = self.flop == value.flop
        is_turn_eq = self.turn == value.turn
        is_river_eq = self.river == value.river
        return is_flop_eq and is_turn_eq and is_river_eq

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
            *cards: Card objects or a single list/tuple of Cards
        
        Returns:
            Table: A new Table instance with the added cards.
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
        
        return Table(total_cards)

    def compare(self, other: Table) -> Table:
        """Compare this Table with another Table and return a new Table with ColorCards indicating matches.
        
        Args:
            other: The Table to compare against
        
        Returns:
            Table: A new Table containing ColorCards ('g'=green, 'y'=yellow, 'e'=grey)
        """
        if not isinstance(other, Table):
            raise ValueError("other must be an instance of Table")
        if len(self.cards) != len(other.cards):
            raise ValueError("Both tables must have the same number of cards to compare")

        green_flop_cards = self.flop & other.flop
        self_remaining_flop = np.array(list(self.flop - green_flop_cards))
        other_remaining_flop = np.array(list(other.flop - green_flop_cards))

        # Pre-allocate color_flop list for better performance
        color_flop = []
        
        # Add green cards first
        for card in green_flop_cards:
            color_flop.append(ColorCard(card.rank, card.suit, 'g'))

        # Handle remaining flop cards
        if self_remaining_flop.size != 0:
            self_ranks = np.array([card.rank for card in self_remaining_flop], dtype=np.int8)
            self_suits = np.array([ord(card.suit) for card in self_remaining_flop], dtype=np.int8)
            other_ranks = np.array([card.rank for card in other_remaining_flop], dtype=np.int8)
            other_suits = np.array([ord(card.suit) for card in other_remaining_flop], dtype=np.int8)

            # Use NumPy broadcasting to compute rank-or-suit matches
            yellow_flags = (
                (self_ranks[:, None] == other_ranks[None, :]) |
                (self_suits[:, None] == other_suits[None, :])
            )
            yellow_mask = np.any(yellow_flags, axis=1)
            
            # Vectorized color assignment - create all ColorCards in one go
            color_chars = np.where(yellow_mask, 'y', 'e')
            
            # Single loop to create ColorCards
            for card, color in zip(self_remaining_flop, color_chars):
                color_flop.append(ColorCard(card.rank, card.suit, color))

        # Handle turn
        if self.turn and other.turn:
            if self.turn == other.turn:
                color_turn = ColorCard(self.turn.rank, self.turn.suit, 'g')
            elif self.turn.is_same_rank(other.turn) or self.turn.is_same_suit(other.turn):
                color_turn = ColorCard(self.turn.rank, self.turn.suit, 'y')
            else:
                color_turn = ColorCard(self.turn.rank, self.turn.suit, 'e')
        else:
            color_turn = None

        # Handle river
        if self.river and other.river:
            if self.river == other.river:
                color_river = ColorCard(self.river.rank, self.river.suit, 'g')
            elif self.river.is_same_rank(other.river) or self.river.is_same_suit(other.river):
                color_river = ColorCard(self.river.rank, self.river.suit, 'y')
            else:
                color_river = ColorCard(self.river.rank, self.river.suit, 'e')
        else:
            color_river = None

        # Build result based on what cards exist
        if color_turn and color_river:
            return Table(*color_flop, color_turn, color_river)
        elif color_turn:
            return Table(*color_flop, color_turn)
        else:
            return Table(*color_flop)
    
    def is_match(self, other: Table) -> bool:
        """Check if this color table could have been produced by comparing with other.
        
        Args:
            other: The Table to check against
        
        Returns:
            bool: True if the colors match what compare() would produce
        """
        if not all(isinstance(card, ColorCard) for card in self.cards):
            raise ValueError("is_match can only be called if this table contains ColorCards")
        if not isinstance(other, Table):
            raise ValueError("other must be an instance of Table")
        if len(self.cards) != len(other.cards):
            raise ValueError("Both tables must have the same number of cards to compare")
        
        # Create a plain Table from self's cards (strip colors)
        plain_cards = tuple(Card(card.rank, card.suit) for card in self.cards)
        plain_table = Table(plain_cards)
        
        # Compare and check if result matches self
        expected = plain_table.compare(other)
        
        # Compare colors efficiently
        return (
            all(sc.color == ec.color for sc, ec in zip(self.flop, expected.flop)) and
            (self.turn.color == expected.turn.color if self.turn else True) and
            (self.river.color == expected.river.color if self.river else True)
        )

    def update_colors(self, colors: list[str]) -> Table:
        """Create a new Table with updated card colors.

        Args:
            colors (list[str]): A list of color codes ('g', 'y', 'e') corresponding to each card.
        
        Returns:
            Table: A new Table instance with updated ColorCards.
        """
        if len(colors) != len(self.cards):
            raise ValueError("Length of colors list must match number of cards in the table")
        if not all(color in ['g', 'y', 'e'] for color in colors):
            raise ValueError("Colors must be one of 'g', 'y', or 'e'")

        updated_cards = [
            ColorCard(card.rank, card.suit, color)
            for card, color in zip(self.cards, colors)
        ]
        
        return Table(updated_cards)
    
    def rank_hand(self, hole: list):
        """Ranks the hand of a given list of cards.

        Args:
            cards (list): A list of Card objects.

        Returns:
            tuple: (rank, tie_breakers, best_hand)
                rank (int): Numerical rank of the hand (1-10, where 10 is Royal Flush)
                tie_breakers (tuple): tuple of ranks used for tie-breaking
                best_hand (tuple): Tuple of Card objects representing the best hand

        Example:
            cards = [Card(10, 'H'), Card('J', 'H'), Card('Q', 'H'), Card('K', 'H'), Card('A', 'H')]
            rank, tie_breakers, best_hand = self.rank_hands(cards)
            print(rank)  # Output: 10 (Royal Flush)
            print(tie_breakers)  # Output: [14] (Ace)
            print(best_hand)  # Output: [10H, JH, QH, KH, AH]
        """
        cards = hole + list(self.cards)
        
        # Count occurrences of each rank
        rank_groups = defaultdict(list)
        for card in cards:
            rank_groups[card.rank].append(card)

        # Group cards by suit
        suit_groups = defaultdict(list)
        for card in cards:
            suit_groups[card.suit].append(card)

        # Check for flush
        flush_cards = None
        for suit, suited_cards in suit_groups.items():
            if len(suited_cards) >= 5:
                flush_cards = sorted(
                    suited_cards, key=lambda card: card.rank, reverse=True
                )
                break

        # Check for straight
        ranks = sorted(set(card.rank for card in cards), reverse=True)
        straight_high_card = None

        # Standard straight check
        for i in range(len(ranks) - 4):
            if ranks[i] - ranks[i + 4] == 4:  # 5 consecutive ranks
                straight_high_card = ranks[i]
                break

        # Special case for A-5-4-3-2 (Ace low straight)
        if not straight_high_card and all(r in ranks for r in [14, 5, 4, 3, 2]):
            straight_high_card = 5

        # Check for straight flush
        if flush_cards and straight_high_card:
            flush_ranks = [c.rank for c in flush_cards]
            best_hand = [
                c
                for c in flush_cards
                if straight_high_card >= c.rank >= straight_high_card - 4
            ][:5]

            # Standard straight flush check
            if straight_high_card != 5 and all(
                r in flush_ranks
                for r in range(straight_high_card - 4, straight_high_card + 1)
            ):
                # Get the 5 cards that form the straight flush
                return 9, (straight_high_card,), tuple(best_hand)

            # A-5-4-3-2 straight flush
            if straight_high_card == 5 and all(
                r in flush_ranks for r in [14, 5, 4, 3, 2]
            ):
                return 9, (5,), tuple(best_hand)

        # Check for four of a kind
        for rank, group in rank_groups.items():
            if len(group) == 4:
                four_of_a_kind = group
                return 8, (rank,), tuple(four_of_a_kind)

        three_ranks = [r for r, group in rank_groups.items() if len(group) == 3]
        pair_ranks = [r for r, group in rank_groups.items() if len(group) == 2]

        # Check for full house
        if (three_ranks and pair_ranks) or len(three_ranks) > 1:
            three_of_a_kind = rank_groups[max(three_ranks)]
            if pair_ranks:
                pair = rank_groups[max(pair_ranks)]
            else:
                second_three = rank_groups[min(three_ranks)]
                pair = second_three[:2]
            best_hand = three_of_a_kind + pair
            return 7, (max(three_ranks), max(pair).rank), tuple(best_hand)

        # Check for flush
        if flush_cards:
            flush_card_hand = flush_cards[:5]
            flush_card_hand_ranks = sorted(
                [c.rank for c in flush_card_hand], reverse=True
            )
            return 6, tuple(flush_card_hand_ranks), tuple(flush_card_hand)

        # Check for straight
        if straight_high_card:
            if straight_high_card == 5 and 14 in ranks:  # A-5-4-3-2
                best_hand = [c for c in cards if c.rank in [14, 5, 4, 3, 2]]
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
            return 5, (straight_high_card,), tuple(best_hand[:5])

        # Check for three of a kind
        if three_ranks:
            three_of_a_kind = rank_groups[max(three_ranks)]
            remaining = sorted(set(cards) - set(three_of_a_kind), reverse=True)
            remaining_ranks = [c.rank for c in remaining]
            return (
                4,
                tuple([three_of_a_kind[0].rank] + remaining_ranks[:2]),
                tuple(three_of_a_kind),
            )

        # Check for two pair
        if len(pair_ranks) >= 2:
            pair_ranks.sort(reverse=True)
            two_pair = rank_groups[pair_ranks[0]] + rank_groups[pair_ranks[1]]
            remaining = sorted(set(cards) - set(two_pair), reverse=True)
            remaining_ranks = [c.rank for c in remaining]
            return 3, tuple(pair_ranks[:2] + remaining_ranks[:1]), tuple(two_pair)

        # Check for one pair
        if pair_ranks:
            pair = rank_groups[pair_ranks[0]]
            remaining = sorted(set(cards) - set(pair), reverse=True)
            remaining_ranks = [c.rank for c in remaining]
            return 2, tuple([pair_ranks[0]] + remaining_ranks[:3]), tuple(pair)

        # High card
        best_hand = sorted(cards, reverse=True)[:5]
        best_hand_ranks = [c.rank for c in best_hand]
        return (
            1,
            tuple(best_hand_ranks),
            tuple([best_hand[0]]),
        )  # Return only the highest card for high card