"""Command-line interface for the Pokle solver.

Provides an interactive CLI for entering player hole cards, hand rankings at
each phase, and iteratively guessing the table configuration based on color
feedback.

This script can be run either as a module (python -m pokle_solver.cli)
or directly as a script (python cli.py).

Functions:
    cli: Main interactive CLI function
"""

# Support both direct execution and module import
if __name__ == "__main__":
    # Running as script - use absolute imports with sys.path manipulation
    import sys
    from pathlib import Path
    
    # Add parent directory to path so we can import pokle_solver
    src_path = Path(__file__).parent.parent
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    from pokle_solver.card import Card
    from pokle_solver.solver import Solver
else:
    # Running as module - use relative imports
    from .card import Card
    from .solver import Solver


def cli():
    player_holes = []
    player_number = 1
    while player_number <= 3:
        hole_str = input(
            f"Enter Player {player_number} hole cards (e.g. 10H KD): "
        ).upper()
        try:
            hole = [Card.from_string(card_str) for card_str in hole_str.split()]
            if len(hole) != 2:
                raise ValueError(
                    f"Please enter exactly two cards for Player {player_number}."
                )
            player_holes.append(hole)
            player_number += 1
        except ValueError as e:
            print(f"Error: {e}")

    p1_hole, p2_hole, p3_hole = player_holes

    game_phase = ("flop", "turn", "river")
    game_phase_number = 0
    hand_ranks_list = []
    while game_phase_number < 3:
        phase = game_phase[game_phase_number]
        ranks_str = input(
            f"Enter player rank of each player's hand in the {phase} (e.g. 2 1 3): "
        )
        hand_ranks = ranks_str.split()
        try:
            if sorted(hand_ranks) != ["1", "2", "3"]:
                raise ValueError("Please enter valid ranks (1, 2, 3) for each player.")
            hand_ranks = [int(rank) for rank in hand_ranks]
            hand_ranks = [i for i, _ in sorted(enumerate(hand_ranks, start=1), key=lambda x: x[1])]
            hand_ranks_list.append(hand_ranks)
            game_phase_number += 1
        except ValueError as e:
            print(f"Error: {e}")

    flop, turn, river = hand_ranks_list

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


if __name__ == "__main__":
    cli()
