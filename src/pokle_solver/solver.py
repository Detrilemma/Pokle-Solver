from collections import defaultdict
from card import Card
from itertools import combinations

MASTER_DECK = [Card(rank, suit) for rank in range(2, 15) for suit in ['H', 'D', 'C', 'S']]

class Solver:
    def __init__(self):
        self.hole_cards = {
            'P1': [Card.from_string('2H'), Card.from_string('3D')],
            'P2': [Card.from_string('KC'), Card.from_string('KH')],
            'P3': [Card.from_string('2C'), Card.from_string('5H')]
        }
        self.current_deck = MASTER_DECK.copy()

        self.flop_hand_ranks = ['P1', 'P2', 'P3']
        self.turn_hand_ranks = ['P1', 'P3', 'P2']
        self.river_hand_ranks = ['P2', 'P3', 'P1']

    @staticmethod
    def rank_hands(cards: list):
        """Ranks the hand of a given list of cards.

        Args:
            cards (list): A list of Card objects.

        Returns:
            tuple: (rank, tie_breakers, best_hand)
                rank (int): Numerical rank of the hand (1-10, where 10 is Royal Flush)
                tie_breakers (list): list of ranks used for tie-breaking
                best_hand (list): List of Card objects representing the best hand

        Example:
            cards = [Card(10, 'H'), Card('J', 'H'), Card('Q', 'H'), Card('K', 'H'), Card('A', 'H')]
            rank, tie_breakers, best_hand = self.rank_hands(cards)
            print(rank)  # Output: 10 (Royal Flush)
            print(tie_breakers)  # Output: [14] (Ace)
            print(best_hand)  # Output: [10H, JH, QH, KH, AH]
        """
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
            best_hand = [c for c in flush_cards if straight_high_card >= c.rank >= straight_high_card-4][:5]

            # Standard straight flush check
            if straight_high_card != 5 and all(r in flush_ranks for r in range(straight_high_card-4, straight_high_card+1)):
                # Get the 5 cards that form the straight flush
                if straight_high_card == 14:
                    return 10, [14], best_hand  # Royal flush
                else:
                    return 9, [straight_high_card], best_hand
            
            # A-5-4-3-2 straight flush
            if straight_high_card == 5 and all(r in flush_ranks for r in [14, 5, 4, 3, 2]):
                return 9, [5], best_hand

        # Check for four of a kind
        for rank, group in rank_groups.items():
            if len(group) == 4:
                four_of_a_kind = group
                return 8, [rank], four_of_a_kind

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
            return 7, [max(three_ranks), max(pair).rank], best_hand

        # Check for flush
        if flush_cards:
            flush_card_hand = flush_cards[:5]
            flush_card_hand_ranks = sorted([c.rank for c in flush_card_hand], reverse=True)
            return 6, flush_card_hand_ranks, flush_card_hand

        # Check for straight
        if straight_high_card:
            if straight_high_card == 5 and 14 in ranks:  # A-5-4-3-2
                best_hand = [c for c in cards if c.rank in [14, 5, 4, 3, 2]]
                # Sort to ensure proper order
                best_hand.sort(key=lambda c: (1 if c.rank == 14 else c.rank), reverse=True)
            else:
                best_hand = sorted([c for c in cards if straight_high_card >= c.rank >= straight_high_card-4], 
                                   reverse=True)
            return 5, [straight_high_card], best_hand[:5]

        # Check for three of a kind
        if three_ranks:
            three_of_a_kind = rank_groups[max(three_ranks)]
            remaining = sorted(set(cards) - set(three_of_a_kind), reverse=True)
            remaining_ranks = [c.rank for c in remaining]
            return 4, [three_of_a_kind[0].rank] + remaining_ranks[:2], three_of_a_kind

        # Check for two pair
        if len(pair_ranks) >= 2:
            pair_ranks.sort(reverse=True)
            two_pair = rank_groups[pair_ranks[0]] + rank_groups[pair_ranks[1]]
            remaining = sorted(set(cards) - set(two_pair), reverse=True)
            remaining_ranks = [c.rank for c in remaining]
            return 3, pair_ranks[:2] + remaining_ranks[:1], two_pair

        # Check for one pair
        if pair_ranks:
            pair = rank_groups[pair_ranks[0]] 
            remaining = sorted(set(cards) - set(pair), reverse=True)
            remaining_ranks = [c.rank for c in remaining]
            return 2, [pair_ranks[0]] + remaining_ranks[:3], pair

        # High card
        best_hand = sorted(cards, reverse=True)[:5]
        best_hand_ranks = [c.rank for c in best_hand]
        return 1, best_hand_ranks, best_hand

    def possible_flops(self):
        """Find all possible flops that maintain the current player rankings.

        Returns:
            list: A list of valid flop combinations.
        """
        hole_card_hashes = {hash(card) for hole in self.hole_cards.values() for card in hole}
        self.current_deck = [card for card in self.current_deck if hash(card) not in hole_card_hashes]
        all_flops = list(combinations(self.current_deck, 3))

        valid_flops = []
        for flop in all_flops:
            current_player_ranks = [] 
            for player, hole in self.hole_cards.items():
                full_hand = hole + list(flop)
                # adds the play name, hand rank, tie breaker list, and best hand
                current_player_ranks.append((player, *self.rank_hands(full_hand)))

            current_player_ranks.sort(reverse=True, key=lambda x: (x[1], x[2]))  # Sort by rank and tie breakers
            current_player_ranks_comparable = [player[0] for player in current_player_ranks]
            if current_player_ranks_comparable == self.flop_hand_ranks:
                valid_flops.append(flop)
        
        return valid_flops

    def possible_turns_rivers(self, flops: list, hand_rankings: list):
        """Find all possible turns that maintain the current player rankings.

        Args:
            flops (list): A list of valid flop combinations.

        Returns:
            list: A list of valid turn combinations.
        """
        valid_turns = []
        for flop in flops:
            turn_deck = set(self.current_deck) - set(flop)
            
            for turn_card in turn_deck:
                full_board = list(flop) + [turn_card]
                
                current_player_ranks = []
                for player, hole in self.hole_cards.items():
                    full_hand = hole + full_board
                    rank, kicker = self.rank_hands(full_hand)
                    composite_rank = rank * 100 + kicker
                    current_player_ranks.append((composite_rank, player))

                current_player_ranks.sort(reverse=True, key=lambda x: x[0])
                current_player_ranks_comparable = [player for _, player in current_player_ranks]
                if current_player_ranks_comparable == hand_rankings:
                    valid_turns.append(tuple(full_board))

        return valid_turns # Print first 5 valid river combinations
    
solver = Solver()
valid_flops = solver.possible_flops()
print(f"Found {len(valid_flops)} valid flops.")
for flop in valid_flops[:5]:
    print(f"Valid Flop: {flop}")