from collections import defaultdict
from card import Card
from itertools import combinations

MASTER_DECK = [Card(rank, suit) for rank in range(2, 15) for suit in ['H', 'D', 'C', 'S']]

class Solver:
    def __init__(self, p1hole: list, p2hole: list, p3hole: list,
                 flop_hand_ranks: list, turn_hand_ranks: list, river_hand_ranks: list):
        
        # Validate hole cards
        for pname, phole in zip(['P1', 'P2', 'P3'], [p1hole, p2hole, p3hole]):
            if not isinstance(phole, list) or len(phole) != 2 or not all(isinstance(card, Card) for card in phole):
                raise ValueError(f"{pname} hole cards must be a list of exactly 2 Card objects.")
        
        for hand_rank_lists in [flop_hand_ranks, turn_hand_ranks, river_hand_ranks]:
            if not isinstance(hand_rank_lists, list) or sorted(hand_rank_lists) != ['P1', 'P2', 'P3']:
                raise ValueError("Hand rank lists must be a permutation of ['P1', 'P2', 'P3']")

        self.hole_cards = {
            'P1': p1hole,
            'P2': p2hole,
            'P3': p3hole
        }

        self.flop_hand_ranks = flop_hand_ranks
        self.turn_hand_ranks = turn_hand_ranks
        self.river_hand_ranks = river_hand_ranks

        self.current_deck = MASTER_DECK.copy()
        self.possible_rivers = []

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
        return 1, best_hand_ranks, [best_hand[0]]  # Return only the highest card for high card

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
                # adds the player name, hand rank, tie breaker list, and best hand
                current_player_ranks.append((player, *self.rank_hands(full_hand)))

            hand_rankings = [(player[1], player[2]) for player in current_player_ranks]
            if len(set(hand_rankings)) < 3:
                continue  # Skip if there are ties in hand rankings

            current_player_ranks.sort(reverse=True, key=lambda x: (x[1], x[2]))  # Sort by rank and tie breakers
            current_player_ranks_comparable = [player[0] for player in current_player_ranks]
            if current_player_ranks_comparable == self.flop_hand_ranks:
                valid_flops.append(flop)
        
        return valid_flops

    def possible_turns_rivers(self, flops: list):
        """Find all possible turns that maintain the current player rankings.

        Args:
            flops (list): A list of valid flop combinations.

        Returns:
            list: A list of valid turn combinations.
        """
        all_hole_cards = {card for hole in self.hole_cards.values() for card in hole}
        
        if len(flops[0]) == 3:
            hand_rankings = self.turn_hand_ranks
            is_river = False
        elif len(flops[0]) == 4:
            hand_rankings = self.river_hand_ranks
            is_river = True
        else:
            raise ValueError("Flops must be a list of 3 (turn) or 4 (river) cards.")

        valid_turns = []
        for flop in flops:
            turn_deck = set(self.current_deck) - set(flop)
            
            for turn_card in turn_deck:
                full_board = list(flop) + [turn_card]
                
                rank_cards_used = set()
                current_player_ranks = []
                for player, hole in self.hole_cards.items():
                    full_hand = hole + full_board
                    # adds the player name, hand rank, tie breaker list, and best hand
                    player_hand = self.rank_hands(full_hand)
                    current_player_ranks.append((player, *player_hand))
                    if is_river and player_hand[0] != 6: # Not a flush
                        rank_cards_used.update(set(player_hand[2]))
                    
                if is_river:
                    rank_cards_used.difference_update(all_hole_cards)
                    if rank_cards_used != set(full_board):
                        continue  # Skip if any board cards are unused in player hands
                
                hand_rankings = [(player[1], player[2]) for player in current_player_ranks]
                if len(set(hand_rankings)) < 3:
                    continue  # Skip if there are ties in hand rankings
                
                current_player_ranks.sort(reverse=True, key=lambda x: (x[1], x[2]))  # Sort by rank and tie breakers
                current_player_ranks_comparable = [player[0] for player in current_player_ranks]
                if current_player_ranks_comparable == hand_rankings:
                    valid_turns.append(full_board)

        return valid_turns
    
    @staticmethod
    def compare_tables(guess: list, answer: list):
        """Compares the guess and the answer and outputs the "color" (green, yellow or grey) of each card based on the wordle-esque game Pokle.
        If two cards in the same position (flop, turn, river) have the same rank and suit, they are "green".
        If the cards in the same position have either a matching rank or suit (but not both), they are "yellow".
        For the cards in the flop (the first three cards), the order of the cards does not matter. ie, 2H 3D 4S is the same as 4S 2H 3D.
        In the flop, two cards in the guess that match either the rank or the suit (but is not a complete match) of one card would both be "yellow".
        However, if one card matches both the rank and suit of one card, it is "green" and the other card would be "grey" (or not colored).
        For example, if the flop of the guess is 2H 3D 4S and the flop of the answer is 4D 5S 2H, the first card would be "green" (2H), the second and third card would be "yellow" (3D matches the D of 4D, and 4S matches the S of 5S).
        Another example, if the flop of the guess is KD KH 3D and the flop of the answer is 7C KS AS, the first and second cards would be "yellow" (KD and KH both match the K of KS), and the third card would be "grey" (3D does not match either the rank or suit of any card in the answer).
        Final example, if the flop of the guess is KS KH 3D and the flop of the answer is 7C KS AS, the first card would be "green" (KS), the second card would be "grey" (KH does not match either the rank or suit of any remaining cards in the answer), and the third card would be "grey" (3D does not match either the rank or suit of any remaining cards in the answer).
        Cards in the turn (the fourth card) and river (the fifth card) are compared by position, so the fourth card of the guess is compared to the fourth card of the answer, and the fifth card of the guess is compared to the fifth card of the answer.

        Args:
            guess (list): The first table to compare.
            answer (list): The second table to compare.

        Returns:
            tuple: A tuple of three sets for the flop in the first position, the turn in the second position, and the river in the third position. 
            Each card string has an underscore and a character representing its color ('_g' for green, '_y' for yellow, and no suffix for grey).
                e.g. ({'2H_g', '3D_y', '4S'}, {'5H_y'}, {'6C_g'})

        Examples:
            guess = [Card.from_string(c) for c in ['4S', 'KD', '7S', '4D', '6S']]
            answer = [Card.from_string(c) for c in ['3H', '9D', 'KS', '6C', '4S']]
            print(compare_tables(guess, answer))
            # Output: ({'4S_y', 'KD_y', '7S_y'}, {'4D'}, {'6S_y'})

            guess = [Card.from_string(c) for c in ['6D', '7D', '9C', 'KC', 'AS']]
            answer = [Card.from_string(c) for c in ['9H', '3S', '6D', 'KC', '9S']]
            print(compare_tables(guess, answer))
            # Output: ({'6D_g', '7D', '9C_y'}, {'KC_g'}, {'AS_y'})

            guess = [Card.from_string(c) for c in ['KS', '9S', 'AS', '4H', '6S']]
            answer = [Card.from_string(c) for c in ['7S', 'KS', 'AH', '4C', '6S']]
            print(compare_tables(guess, answer))
            # Output: ({'KS_g', '9S_y', 'AS_y'}, {'4H_y'}, {'6S_g'})
        """
        # Validate inputs
        if not isinstance(guess, list) or not isinstance(answer, list):
            raise ValueError("Guess and answer must be lists of exactly 5 Card objects.")
        if len(guess) != 5 or len(answer) != 5:
            raise ValueError("Guess and answer must be lists of exactly 5 Card objects.")
        if not all(isinstance(c, Card) for c in guess) or not all(isinstance(c, Card) for c in answer):
            raise ValueError("All elements in guess and answer must be Card instances.")
        
        answer_flop = answer[:3]
        flop_result = set()
        
        for g_card in guess[:3]:
            found_match = False
            for a_card in range(len(answer_flop)):
                if g_card == answer_flop[a_card] and g_card.is_same_suit(answer_flop[a_card]):
                    flop_result.add(f"{g_card}_g")  # Green
                    flop_result.discard(f"{g_card}_y")  # Remove any yellow if previously added
                    answer_flop[a_card] = Card()  # Mark as used
                    found_match = True
                    break
                elif g_card == answer_flop[a_card] or g_card.is_same_suit(answer_flop[a_card]):
                    flop_result.add(f"{g_card}_y")  # Yellow
                    found_match = True
                    # No need to mark as used for yellow
            if not found_match:
                flop_result.add(f"{g_card}")  # Grey (no suffix)

        turn_result = set()
        if guess[3] == answer[3] and guess[3].is_same_suit(answer[3]):
            turn_result.add(f"{guess[3]}_g")  # Green
        elif guess[3] == answer[3] or guess[3].is_same_suit(answer[3]):
            turn_result.add(f"{guess[3]}_y")  # Yellow
        else:
            turn_result.add(f"{guess[3]}")  # Grey

        river_result = set()
        if guess[4] == answer[4] and guess[4].is_same_suit(answer[4]):
            river_result.add(f"{guess[4]}_g")  # Green
        elif guess[4] == answer[4] or guess[4].is_same_suit(answer[4]):
            river_result.add(f"{guess[4]}_y")  # Yellow
        else:
            river_result.add(f"{guess[4]}")  # Grey

        return flop_result, turn_result, river_result

    def solve(self):
        """Find all possible board runouts that maintain the current player rankings.

        Returns:
            list: A list of valid board runouts.
        """
        possible_flops = self.possible_flops()
        possible_turns = self.possible_turns_rivers(possible_flops)
        self.possible_rivers = self.possible_turns_rivers(possible_turns)
            
        return self.possible_rivers
    
    def print_game(self, river: list):
        """Prints the game state for a given river."""
        if not self.possible_rivers:
            raise ValueError("No possible rivers calculated. Please run solve() first.")
        if len(river) != 5 or not all(isinstance(card, Card) for card in river):
            raise ValueError("River must be a list of exactly 5 Card objects.")
        if river not in self.possible_rivers:
            raise ValueError("Provided river is not in the list of possible rivers.")
        
        hand_rank_symbols = {1: 'HC', 2: '1P', 3: '2P', 4: '3K', 5: 'St', 6: 'Fl', 7: 'FH', 8: '4K', 9: 'SF'}
        p1_0 = str(self.hole_cards['P1'][0]).ljust(3)
        p2_0 = str(self.hole_cards['P2'][0]).ljust(3)
        p3_0 = str(self.hole_cards['P3'][0]).ljust(3)
        p1_1 = str(self.hole_cards['P1'][1]).ljust(3)
        p2_1 = str(self.hole_cards['P2'][1]).ljust(3)
        p3_1 = str(self.hole_cards['P3'][1]).ljust(3)
        p1_flop = hand_rank_symbols[self.rank_hands(self.hole_cards['P1'] + river[:3])[0]]
        p2_flop = hand_rank_symbols[self.rank_hands(self.hole_cards['P2'] + river[:3])[0]]
        p3_flop = hand_rank_symbols[self.rank_hands(self.hole_cards['P3'] + river[:3])[0]]
        p1_turn = hand_rank_symbols[self.rank_hands(self.hole_cards['P1'] + river[:4])[0]]
        p2_turn = hand_rank_symbols[self.rank_hands(self.hole_cards['P2'] + river[:4])[0]]
        p3_turn = hand_rank_symbols[self.rank_hands(self.hole_cards['P3'] + river[:4])[0]]
        p1_river = hand_rank_symbols[self.rank_hands(self.hole_cards['P1'] + river)[0]]
        p2_river = hand_rank_symbols[self.rank_hands(self.hole_cards['P2'] + river)[0]]
        p3_river = hand_rank_symbols[self.rank_hands(self.hole_cards['P3'] + river)[0]]

        print("Pokle Solver Results")
        print(f"         P1   P2   P3")
        print(f"       ---- ---- ----")
        print(f"        {p1_0}  {p2_0}  {p3_0}")
        print(f"        {p1_1}  {p2_1}  {p3_1}")
        print(f" flop:  {p1_flop}   {p2_flop}   {p3_flop}")
        print(f" turn:  {p1_turn}   {p2_turn}   {p3_turn}")
        print(f"river:  {p1_river}   {p2_river}   {p3_river}")
        print(f"|---flop---|turn|river|")
        print(f"| {river[0]} {river[1]} {river[2]} | {river[3]} | {river[4]}  |")
        print()


