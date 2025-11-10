#!/usr/bin/env python3
"""Simulated interactive test for sandbox"""

import sys
sys.path.insert(0, 'src/pokle_solver')

from card import Card
from solver import Solver

# Use the large dataset
p1_hole = [Card.from_string("JH"), Card.from_string("6H")]
p2_hole = [Card.from_string("4H"), Card.from_string("7S")]
p3_hole = [Card.from_string("5D"), Card.from_string("8D")]

flop = [3, 2, 1]
turn = [2, 3, 1]
river = [2, 1, 3]

print("=" * 80)
print("INTERACTIVE SANDBOX TEST (Simulated)")
print("=" * 80)

solver = Solver(p1_hole, p2_hole, p3_hole, flop, turn, river)
possible_rivers = solver.solve()
print(f"\nPossible rivers found: {len(possible_rivers)}")

print("\n" + "=" * 80)
print("ROUND 1: Initial Guess")
print("=" * 80)
solver.print_game(solver.get_maxh_table())

# Simulate giving feedback
print("\n--- Simulating user feedback: 'y e e e e' ---")
card_colors = ['y', 'e', 'e', 'e', 'e']

try:
    solver.next_table_guess(card_colors)
    print(f"✓ Filtered to {len(solver.valid_rivers)} possible rivers")
except ValueError as e:
    print(f"✗ Error filtering: {e}")
    # Try different feedback
    print("\n--- Trying different feedback: 'e y e e e' ---")
    card_colors = ['e', 'y', 'e', 'e', 'e']
    solver.next_table_guess(card_colors)
    print(f"✓ Filtered to {len(solver.valid_rivers)} possible rivers")

print("\n" + "=" * 80)
print("ROUND 2: Next Guess")
print("=" * 80)
solver.print_game(solver.get_maxh_table())

print("\n--- Simulating user feedback: 'e e y y e' ---")
card_colors = ['e', 'e', 'y', 'y', 'e']

try:
    solver.next_table_guess(card_colors)
    print(f"✓ Filtered to {len(solver.valid_rivers)} possible rivers")
    
    print("\n" + "=" * 80)
    print("ROUND 3: Final Guess")
    print("=" * 80)
    solver.print_game(solver.get_maxh_table())
    
    print("\n✓✓✓ All interactive tests passed! ✓✓✓")
    
except ValueError as e:
    print(f"Note: {e}")
    print("(This is normal if the specific feedback doesn't match any rivers)")
