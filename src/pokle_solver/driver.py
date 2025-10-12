from card import Card
from collections import defaultdict
from solver import Solver

def driver():
    hole_cards_1011 = {
            'P1': [Card.from_string('2H'), Card.from_string('3D')],
            'P2': [Card.from_string('KC'), Card.from_string('KH')],
            'P3': [Card.from_string('2C'), Card.from_string('5H')]
        }

    flop_hand_ranks_1011 = ['P1', 'P2', 'P3']
    turn_hand_ranks_1011 = ['P1', 'P3', 'P2']
    river_hand_ranks_1011 = ['P2', 'P3', 'P1']

    
    
if __name__ == "__main__":
    driver()
