from card import Card
from collections import defaultdict
from solver import Solver

def driver():

    # Create a solver instance
    solver = Solver()

    # Test different poker hand combinations
    test_hands = [
        # Royal Flush
        [Card('A', 'H'), Card('K', 'H'), Card('Q', 'H'), Card('J', 'H'), Card('10', 'H'), Card('3', 'D'), Card('5', 'S')],
        
        # Straight Flush
        [Card('9', 'S'), Card('8', 'S'), Card('7', 'S'), Card('6', 'S'), Card('5', 'S'), Card('2', 'H'), Card('4', 'D')],
        
        # Four of a Kind
        [Card('K', 'H'), Card('K', 'D'), Card('K', 'S'), Card('K', 'C'), Card('2', 'H'), Card('3', 'D'), Card('4', 'S')],
        
        # Full House
        [Card('A', 'H'), Card('A', 'D'), Card('A', 'S'), Card('8', 'H'), Card('8', 'D'), Card('3', 'C'), Card('4', 'S')],
        
        # Flush
        [Card('K', 'D'), Card('J', 'D'), Card('9', 'D'), Card('6', 'D'), Card('3', 'D'), Card('2', 'H'), Card('4', 'S')],
        
        # Straight
        [Card('10', 'H'), Card('9', 'S'), Card('8', 'D'), Card('7', 'C'), Card('6', 'H'), Card('2', 'D'), Card('4', 'S')],
        
        # Three of a Kind
        [Card('7', 'H'), Card('7', 'D'), Card('7', 'S'), Card('K', 'H'), Card('2', 'D'), Card('3', 'C'), Card('4', 'S')],
        
        # Two Pair
        [Card('A', 'H'), Card('A', 'D'), Card('8', 'S'), Card('8', 'H'), Card('4', 'D'), Card('3', 'C'), Card('2', 'H')],
        
        # One Pair
        [Card('10', 'H'), Card('10', 'D'), Card('9', 'S'), Card('6', 'H'), Card('4', 'C'), Card('3', 'D'), Card('2', 'S')],
        
        # High Card
        [Card('A', 'H'), Card('J', 'D'), Card('8', 'S'), Card('5', 'H'), Card('3', 'C'), Card('2', 'D'), Card('4', 'S')],
    ]

    # Rank all hands and display results
    for hand in test_hands:
        rank, tie_breakers, best_hand = solver.rank_hands(hand)
        print(f"Hand: {hand} => Rank: {rank},\n Tie Breakers: {tie_breakers}, Best Hand: {best_hand}\n")

if __name__ == "__main__":
    driver()
