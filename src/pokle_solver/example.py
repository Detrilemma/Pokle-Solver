from card import Card
from collections import defaultdict
from solver import Solver

def example():
    hole_cards_1011 = {
            'P1': [Card.from_string('2H'), Card.from_string('3D')],
            'P2': [Card.from_string('KC'), Card.from_string('KH')],
            'P3': [Card.from_string('2C'), Card.from_string('5H')]
        }

    flop_hand_ranks_1011 = ['P1', 'P2', 'P3']
    turn_hand_ranks_1011 = ['P1', 'P3', 'P2']
    river_hand_ranks_1011 = ['P2', 'P3', 'P1']

    hole_cards_1012 = {
            'P1': [Card.from_string('6D'), Card.from_string('6S')],
            'P2': [Card.from_string('2C'), Card.from_string('3S')],
            'P3': [Card.from_string('8C'), Card.from_string('8D')]
        }

    flop_hand_ranks_1012 = ['P2', 'P1', 'P3']
    turn_hand_ranks_1012 = ['P1', 'P2', 'P3']
    river_hand_ranks_1012 = ['P1', 'P3', 'P2']

    solver_1011 = Solver(hole_cards_1011['P1'], hole_cards_1011['P2'], hole_cards_1011['P3'],
                         flop_hand_ranks_1011, turn_hand_ranks_1011, river_hand_ranks_1011)
    possible_rivers_1011 = solver_1011.solve()
    print(f"Possible rivers for test case 1011: {len(possible_rivers_1011)}")

    solver_1011.print_game(possible_rivers_1011[0])

    solver_1012 = Solver(hole_cards_1012['P1'], hole_cards_1012['P2'], hole_cards_1012['P3'],
                         flop_hand_ranks_1012, turn_hand_ranks_1012, river_hand_ranks_1012)
    possible_rivers_1012 = solver_1012.solve()
    print(f"Possible rivers for test case 1012: {len(possible_rivers_1012)}")
    for river in possible_rivers_1012[:300]:
        print(river)

    solver_1012.print_game(possible_rivers_1012[0])
    
if __name__ == "__main__":
    example()
