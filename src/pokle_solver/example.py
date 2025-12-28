from card import Card
from solver import Solver
import numpy as np

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


def demo():
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
            temp_hand_ranks = hand_ranks.copy()
            hand_ranks[:] = [
                temp_hand_ranks.index(i) + 1 for i in range(1, len(temp_hand_ranks) + 1)
            ]
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

def proving_ground():
    
    def organize_flop(preceding_table, current_table):
        """Organize flop cards based on matching priority: exact > rank > suit > remaining."""
        preceding_flop = preceding_table[:3].copy()
        current_flop = current_table[:3].copy()
        updated_flop = [None] * 3
        
        # Phase 1: Exact card matches (highest priority)
        for i, prev_card in enumerate(preceding_flop):
            if prev_card in current_flop:
                updated_flop[i] = prev_card
                current_flop.remove(prev_card)
                preceding_flop[i] = None  # Mark as matched
        
        # Phase 2: Rank matches (second priority)
        for i, prev_card in enumerate(preceding_flop):
            if prev_card is None or updated_flop[i] is not None:
                continue
            
            match_idx = next((j for j, curr_card in enumerate(current_flop) 
                            if curr_card.rank == prev_card.rank), None)
            if match_idx is not None:
                updated_flop[i] = current_flop.pop(match_idx)
        
        # Phase 3: Suit matches (third priority)
        for i, prev_card in enumerate(preceding_flop):
            if prev_card is None or updated_flop[i] is not None:
                continue
            
            match_idx = next((j for j, curr_card in enumerate(current_flop) 
                            if curr_card.suit == prev_card.suit), None)
            if match_idx is not None:
                updated_flop[i] = current_flop.pop(match_idx)
        
        # Phase 4: Fill remaining slots with leftover cards
        for i in range(3):
            if updated_flop[i] is None and current_flop:
                updated_flop[i] = current_flop.pop(0)
        
        return updated_flop + current_table[3:]
    
    def reverse_org_colors(organized_table, current_table, table_colors):
        """Reverse organize colors to match original table order."""
        # Create a mapping of card -> color from organized table
        color_map = dict(zip(organized_table, table_colors))
        # Map each current table card to its color
        return [color_map[card] for card in current_table]
    
    current_t = [Card.from_string(c) for c in ['KS', '9D', 'KH', '6C', '4S']]
    preceding_t = [Card.from_string(c) for c in  ['4S', 'KD', '7S', '4D', '6S']]
    print(f"  Current Table: {[str(card) for card in current_t]}")
    print(f"Preceding Table: {[str(card) for card in preceding_t]}")
    print(f"Organized Table: {[str(card) for card in organize_flop(preceding_t, current_t)]}")

if __name__ == "__main__":
    sandbox()
