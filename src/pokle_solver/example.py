from numpy import place
from card import Card
from solver import Solver
import pandas as pd


def example():
    hole_cards_1011 = {
        "P1": [Card.from_string("2H"), Card.from_string("3D")],
        "P2": [Card.from_string("KC"), Card.from_string("KH")],
        "P3": [Card.from_string("2C"), Card.from_string("5H")],
    }

    flop_hand_ranks_1011 = [1, 2, 3]
    turn_hand_ranks_1011 = [1, 3, 2]
    river_hand_ranks_1011 = [2, 3, 1]

    hole_cards_1012 = {
        "P1": [Card.from_string("6D"), Card.from_string("6S")],
        "P2": [Card.from_string("2C"), Card.from_string("3S")],
        "P3": [Card.from_string("8C"), Card.from_string("8D")],
    }

    flop_hand_ranks_1012 = [2, 1, 3]
    turn_hand_ranks_1012 = [1, 2, 3]
    river_hand_ranks_1012 = [1, 3, 2]

    # solver_1011 = Solver(hole_cards_1011['P1'], hole_cards_1011['P2'], hole_cards_1011['P3'],
    #                      flop_hand_ranks_1011, turn_hand_ranks_1011, river_hand_ranks_1011)
    # possible_rivers_1011 = solver_1011.solve()
    # print(f"Possible rivers for test case 1011: {len(possible_rivers_1011)}")

    # solver_1011.print_game(possible_rivers_1011[0])

    solver_1012 = Solver(
        hole_cards_1012["P1"],
        hole_cards_1012["P2"],
        hole_cards_1012["P3"],
        flop_hand_ranks_1012,
        turn_hand_ranks_1012,
        river_hand_ranks_1012,
    )
    possible_rivers_1012 = solver_1012.solve()
    print(f"Possible rivers for test case 1012: {len(possible_rivers_1012)}")

    # for river in possible_rivers_1012:
    #     print(river)

    # first guess
    first_guess = solver_1012.get_maxh_table()
    print(first_guess)
    comparisons_matrix = getattr(solver_1012, "comparisons_matrix")
    print(comparisons_matrix["(4H, 5H, 6H, 4S, 7D)"].value_counts())

    # second guess
    print(len(solver_1012.next_table_guess(["_y", "_y", "_g", "", "_y"])))

def sandbox():
    # p1_hole = [Card.from_string("6H"), Card.from_string("8H")]
    # p2_hole = [Card.from_string("QS"), Card.from_string("JC")]
    # p3_hole = [Card.from_string("4H"), Card.from_string("JD")]

    # flop = [2, 1, 3]
    # turn = [2, 3, 1]
    # river = [3, 2, 1]

    # slow output for testing
    p1_hole = [Card.from_string("KH"), Card.from_string("6S")]
    p2_hole = [Card.from_string("8C"), Card.from_string("8H")]
    p3_hole = [Card.from_string("4H"), Card.from_string("9S")]

    flop = [2, 3, 1]
    turn = [3, 2, 1]
    river = [3, 1, 2]

    # fast example
    # p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
    # p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
    # p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

    # flop = [2, 1, 3]
    # turn = [1, 3, 2]
    # river = [2, 1, 3]


    solver = Solver(p1_hole, p2_hole, p3_hole, flop, turn, river)
    possible_rivers = solver.solve()
    print(f"Possible rivers found: {len(possible_rivers)}")
    solver.print_game(solver.get_maxh_table())

    card_colors = ['e' for _ in range(5)]
    is_all_green = False
    while not is_all_green:
        color_input = input("Enter color feedback for river cards (g=green, y=yellow, e=grey), e.g. g y e e g: ").lower()
        card_colors = color_input.split()
        try:
            if len(card_colors) != 5 or not all(color in ['g', 'y', 'e'] for color in card_colors):
                raise ValueError("Please enter exactly 5 colors using 'g', 'y', or 'e'.")
            solver.next_table_guess(card_colors)
            print(f"Possible rivers remaining: {len(solver.valid_rivers)}")
            is_all_green = all(color == 'g' for color in card_colors)
            solver.print_game(solver.get_maxh_table(), is_win=is_all_green)
        except ValueError as e:
            print(f"Error: {e}")

def demo():
    player_holes = []
    player_number = 1
    while player_number <= 3:
        hole_str = input(f"Enter Player {player_number} hole cards (e.g. 10H KD): ").upper()
        try:
            hole = [Card.from_string(card_str) for card_str in hole_str.split()]
            if len(hole) != 2:
                raise ValueError(f"Please enter exactly two cards for Player {player_number}.")
            player_holes.append(hole)
            player_number += 1
        except ValueError as e:
            print(f"Error: {e}")
        
    p1_hole, p2_hole, p3_hole = player_holes

    game_phase = ('flop', 'turn', 'river')
    game_phase_number = 0
    hand_ranks_list = []
    while game_phase_number < 3:
        phase = game_phase[game_phase_number]
        ranks_str = input(f"Enter player rank of each player's hand in the {phase} (e.g. 2 1 3): ")
        hand_ranks = ranks_str.split()
        try:
            if sorted(hand_ranks) != ['1', '2', '3']:
                raise ValueError("Please enter valid ranks (1, 2, 3) for each player.")
            hand_ranks = [int(rank) for rank in hand_ranks]
            temp_hand_ranks = hand_ranks.copy()
            hand_ranks[:] = [temp_hand_ranks.index(i) + 1 for i in range(1, len(temp_hand_ranks) + 1)]
            hand_ranks_list.append(hand_ranks)
            game_phase_number += 1
        except ValueError as e:
            print(f"Error: {e}")

    flop, turn, river = hand_ranks_list

    solver = Solver(p1_hole, p2_hole, p3_hole, flop, turn, river)
    possible_rivers = solver.solve()
    print(f"Possible rivers found: {len(possible_rivers)}")
    solver.print_game(solver.get_maxh_table())

    card_colors = ['e' for _ in range(5)]
    is_all_green = False
    while not is_all_green:
        color_input = input("Enter color feedback for river cards (g=green, y=yellow, e=grey), e.g. g y e e g: ").lower()
        card_colors = color_input.split()
        try:
            if len(card_colors) != 5 or not all(color in ['g', 'y', 'e'] for color in card_colors):
                raise ValueError("Please enter exactly 5 colors using 'g', 'y', or 'e'.")
            solver.next_table_guess(card_colors)
            print(f"Possible rivers remaining: {len(solver.valid_rivers)}")
            is_all_green = all(color == 'g' for color in card_colors)
            solver.print_game(solver.get_maxh_table(), is_win=is_all_green)
        except ValueError as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    sandbox()
    
