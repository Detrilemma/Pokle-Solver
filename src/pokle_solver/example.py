from card import Card
from solver import Solver
import cProfile



def sandbox():
    # p1_hole = [Card.from_string("6H"), Card.from_string("8H")]
    # p2_hole = [Card.from_string("QS"), Card.from_string("JC")]
    # p3_hole = [Card.from_string("4H"), Card.from_string("JD")]

    # flop = [2, 1, 3]
    # turn = [2, 3, 1]
    # river = [3, 2, 1]

    # slow output for testing
    # p1_hole = [Card.from_string("KH"), Card.from_string("6S")]
    # p2_hole = [Card.from_string("8C"), Card.from_string("8H")]
    # p3_hole = [Card.from_string("4H"), Card.from_string("9S")]

    # flop = [2, 3, 1]
    # turn = [3, 2, 1]
    # river = [3, 1, 2]

    # fast example
    # p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
    # p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
    # p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

    # flop = [2, 1, 3]
    # turn = [1, 3, 2]
    # river = [2, 1, 3]

    #  super slow output for testing
    # p1_hole = [Card.from_string("JH"), Card.from_string("6H")]
    # p2_hole = [Card.from_string("4H"), Card.from_string("7S")]
    # p3_hole = [Card.from_string("5D"), Card.from_string("8D")]

    # flop = [3, 2, 1]
    # turn = [2, 3, 1]
    # river = [2, 1, 3]

    # recent example 12/14
    # p1_hole = [Card.from_string("4D"), Card.from_string("AH")]
    # p2_hole = [Card.from_string("8C"), Card.from_string("QS")]
    # p3_hole = [Card.from_string("9D"), Card.from_string("JS")]

    # flop = [3, 2, 1]
    # turn = [2, 3, 1]
    # river = [3, 2, 1]

    # recent example 12/25
    p1_hole = [Card.from_string("7C"), Card.from_string("9D")]
    p2_hole = [Card.from_string("KH"), Card.from_string("KS")]
    p3_hole = [Card.from_string("8D"), Card.from_string("4S")]

    flop = [1, 2, 3]
    turn = [3, 1, 2]
    river = [2, 3, 1]

    solver = Solver(p1_hole, p2_hole, p3_hole, flop, turn, river)
    possible_tables = solver.solve()
    print(f"Possible tables found: {len(possible_tables)}")
    solver.print_game(solver.get_maxh_table())

    card_colors = ["e" for _ in range(5)]
    is_all_green = False
    while not is_all_green:
        color_input = input(
            "Enter color feedback for river cards (g=green, y=yellow, e=grey), e.g. g y e e g: "
        ).lower()
        card_colors = color_input.split()
        try:
            if len(card_colors) != 5 or not all(
                color in ["g", "y", "e"] for color in card_colors
            ):
                raise ValueError(
                    "Please enter exactly 5 colors using 'g', 'y', or 'e'."
                )
            solver.next_table_guess(card_colors)
            print(f"Possible tables remaining: {len(solver.valid_tables)}")
            is_all_green = all(color == "g" for color in card_colors)
            solver.print_game(solver.get_maxh_table())
        except ValueError as e:
            print(f"Error: {e}")

def profile():
    # p1_hole = [Card.from_string("6H"), Card.from_string("8H")]
    # p2_hole = [Card.from_string("QS"), Card.from_string("JC")]
    # p3_hole = [Card.from_string("4H"), Card.from_string("JD")]

    # flop = [2, 1, 3]
    # turn = [2, 3, 1]
    # river = [3, 2, 1]

    # slow output for testing
    # p1_hole = [Card.from_string("KH"), Card.from_string("6S")]
    # p2_hole = [Card.from_string("8C"), Card.from_string("8H")]
    # p3_hole = [Card.from_string("4H"), Card.from_string("9S")]

    # flop = [2, 3, 1]
    # turn = [3, 2, 1]
    # river = [3, 1, 2]

    # fast example
    # p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
    # p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
    # p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

    # flop = [2, 1, 3]
    # turn = [1, 3, 2]
    # river = [2, 1, 3]

    #  super slow output for testing
    # p1_hole = [Card.from_string("JH"), Card.from_string("6H")]
    # p2_hole = [Card.from_string("4H"), Card.from_string("7S")]
    # p3_hole = [Card.from_string("5D"), Card.from_string("8D")]

    # flop = [3, 2, 1]
    # turn = [2, 3, 1]
    # river = [2, 1, 3]

    # recent example 12/14
    # p1_hole = [Card.from_string("4D"), Card.from_string("AH")]
    # p2_hole = [Card.from_string("8C"), Card.from_string("QS")]
    # p3_hole = [Card.from_string("9D"), Card.from_string("JS")]

    # flop = [3, 2, 1]
    # turn = [2, 3, 1]
    # river = [3, 2, 1]

    # recent example 12/25
    p1_hole = [Card.from_string("7C"), Card.from_string("9D")]
    p2_hole = [Card.from_string("KH"), Card.from_string("KS")]
    p3_hole = [Card.from_string("8D"), Card.from_string("4S")]

    flop = [1, 2, 3]
    turn = [3, 1, 2]
    river = [2, 3, 1]

    solver = Solver(p1_hole, p2_hole, p3_hole, flop, turn, river)
    possible_tables = solver.solve()
    print(f"Possible tables found: {len(possible_tables)}")
    solver.print_game(solver.get_maxh_table())


if __name__ == "__main__":
    profile()
