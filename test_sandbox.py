#!/usr/bin/env python3
"""Test script to verify next_table_guess works with sampling"""

import sys
sys.path.insert(0, 'src/pokle_solver')

from card import Card
from solver import Solver

# Use the large dataset that triggers sampling
p1_hole = [Card.from_string("JH"), Card.from_string("6H")]
p2_hole = [Card.from_string("4H"), Card.from_string("7S")]
p3_hole = [Card.from_string("5D"), Card.from_string("8D")]

flop = [3, 2, 1]
turn = [2, 3, 1]
river = [2, 1, 3]

print("Creating solver...")
solver = Solver(p1_hole, p2_hole, p3_hole, flop, turn, river)

print("Solving...")
possible_rivers = solver.solve()
print(f"Possible rivers found: {len(possible_rivers)}")

print("\nGetting max entropy table (will use sampling)...")
max_table = solver.get_maxh_table()
print(f"Selected table: {max_table}")

print("\nTesting next_table_guess with feedback...")
# Simulate user feedback - let's give some realistic feedback
# The selected table is printed above, let's say first card matches rank or suit (yellow)
# and others are wrong
card_colors = ['y', 'e', 'e', 'e', 'e']

print(f"Selected table: {max_table}")
print(f"Giving feedback: {card_colors}")

try:
    filtered_rivers = solver.next_table_guess(card_colors)
    print(f"✓ Success! Filtered to {len(filtered_rivers)} possible rivers")
    
    # Get next guess
    print("\nGetting next max entropy table...")
    next_table = solver.get_maxh_table()
    print(f"Next suggested table: {next_table}")
    print("\n✓ All tests passed!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    
    # Debug: Let's see what comparisons look like
    print("\nDEBUG: Let's check a few comparison results...")
    for i, river in enumerate(solver.valid_rivers[:5]):
        comp = max_table.compare(river)
        print(f"  River {i+1}: {river}")
        print(f"    Comparison: {comp}")
    sys.exit(1)
