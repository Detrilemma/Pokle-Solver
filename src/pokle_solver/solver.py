from card import Card

class Solver:
    def __init__(self):
        self.p1_hole = []
        self.p2_hole = []
        self.p3_hole = []

        self.flop_hand_ranks = []
        self.turn_hand_ranks = []
        self.river_hand_ranks = []

    def rank_hands(cards: list):
        """Ranks the hand of a given list of cards.

        Args:
            cards (list): A list of Card objects.

        Returns:
            tuple: (rank, kicker_rank)
                rank (int): Numerical rank of the hand (1-10, where 10 is Royal Flush)
                kicker_rank (int): Rank of the kicker card

        Example:
            cards = [Card(10, 'H'), Card(11, 'H'), Card(12, 'H'), Card(13, 'H'), Card(14, 'H')]
            rank, kicker_rank = self.rank_hands(cards)
            print(rank)  # Output: 10 (Royal Flush)
            print(kicker_rank)  # Output: 14 (Ace)
        """
        # Count occurrences of each rank
        rank_counts = {}
        for card in cards:
            rank_counts[card.rank] = rank_counts.get(card.rank, 0) + 1

        # Group cards by suit
        suit_groups = {}
        for card in cards:
            if card.suit not in suit_groups:
                suit_groups[card.suit] = []
            suit_groups[card.suit].append(card)

        # Check for flush
        flush_cards = None
        for suit, suited_cards in suit_groups.items():
            if len(suited_cards) >= 5:
                flush_cards = sorted(suited_cards, key=lambda card: card.rank, reverse=True)
                break

        # Check for straight
        ranks = sorted(set(card.rank for card in cards), reverse=True)
        straight_high_card = None

        # Standard straight check
        for i in range(len(ranks) - 4):
            if ranks[i] - ranks[i+4] == 4:  # 5 consecutive ranks
                straight_high_card = ranks[i]
                break

        # Special case for A-5-4-3-2 (Ace low straight)
        if not straight_high_card and all(r in ranks for r in [14, 5, 4, 3, 2]):
            straight_high_card = 5

        # Check for straight flush
        if flush_cards and straight_high_card:
            flush_ranks = [c.rank for c in flush_cards]
            
            # Standard straight flush check
            if straight_high_card != 5 and all(r in flush_ranks for r in range(straight_high_card-4, straight_high_card+1)):
                if straight_high_card == 14:
                    return 10, 14 # Royal flush
                else:
                    return 9, straight_high_card
            
            # A-5-4-3-2 straight flush
            if straight_high_card == 5 and all(r in flush_ranks for r in [14, 5, 4, 3, 2]):
                return 9, 5

        # Check for four of a kind
        for rank, count in rank_counts.items():
            if count == 4:
                return 8, rank

        three_ranks = [r for r, c in rank_counts.items() if c == 3]
        pair_ranks = [r for r, c in rank_counts.items() if c == 2]

        # Check for full house
        three_ranks.sort(reverse=True)
        if (three_ranks and pair_ranks) or len(three_ranks) > 1:
            return 7, three_ranks[0]

        # Check for flush
        if flush_cards:
            return 6, flush_cards[0].rank

        # Check for straight
        if straight_high_card:
            return 5, straight_high_card

        # Check for three of a kind
        if three_ranks:
            return 4, three_ranks[0]

        # Check for two pair
        if len(pair_ranks) >= 2:
            pair_ranks.sort(reverse=True)
            return 3, pair_ranks[0]

        # Check for one pair
        if pair_ranks:
            return 2, pair_ranks[0]

        # High card
        return 1, ranks[0]