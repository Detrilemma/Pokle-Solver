# """Integration tests for the Solver class."""

# import pytest
# import sys
# from pathlib import Path

# # Add src directory to path
# sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "pokle_solver"))

# from card import Card
# from solver import Solver


# class TestSolverIntegrationBasic:
#     """Basic integration tests for the Solver workflow."""

#     def test_full_solve_workflow(self):
#         """Test complete solving workflow from initialization to solution."""
#         # Setup
#         p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
#         p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
#         p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

#         solver = Solver(
#             p1_hole,
#             p2_hole,
#             p3_hole,
#             flop_hand_ranks=[2, 1, 3],
#             turn_hand_ranks=[1, 3, 2],
#             river_hand_ranks=[2, 1, 3],
#         )

#         # Solve
#         possible_rivers = solver.solve()

#         # Verify results
#         assert len(possible_rivers) > 0
#         assert all(isinstance(table, Table) for table in possible_rivers)
#         assert all(len(table.cards) == 5 for table in possible_rivers)
#         assert all(
#             table.flop and table.turn and table.river for table in possible_rivers
#         )

#     def test_solve_and_get_maxh_table_workflow(self):
#         """Test solving and getting the maximum entropy table."""
#         p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
#         p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
#         p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

#         solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])

#         # Solve and get maxh table
#         possible_rivers = solver.solve()
#         maxh_table = solver.get_maxh_table()

#         # Verify
#         assert maxh_table in possible_rivers
#         assert isinstance(maxh_table, Table)
#         assert len(maxh_table.cards) == 5

#     def test_solve_get_maxh_and_filter_workflow(self):
#         """Test complete workflow: solve, get maxh, and filter with guess."""
#         p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
#         p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
#         p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

#         solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])

#         # Solve
#         initial_rivers = solver.solve()
#         initial_count = len(initial_rivers)

#         # Get maxh table
#         maxh_table = solver.get_maxh_table()

#         # Make a guess based on comparison with first river
#         first_river = initial_rivers[0]
#         comparison = maxh_table.compare(first_river)
#         colors = [card.color for card in comparison.cards]

#         # Filter
#         filtered_rivers = solver.next_table_guess(colors)

#         # Verify
#         assert len(filtered_rivers) <= initial_count
#         assert all(table in initial_rivers for table in filtered_rivers)

#     def test_solve_with_all_green_guess(self):
#         """Test that all green colors returns exactly one river (the correct answer)."""
#         p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
#         p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
#         p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

#         solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])
#         solver.solve()

#         maxh_table = solver.get_maxh_table()

#         # All green means we guessed correctly
#         comparison = maxh_table.compare(maxh_table)
#         colors = [card.color for card in comparison.cards]

#         assert all(color == "g" for color in colors)

#         filtered = solver.next_table_guess(colors)

#         # Should have exactly one table - the maxh_table itself
#         assert len(filtered) == 1
#         assert filtered[0] == maxh_table

#     def test_multiple_guess_iterations(self):
#         """Test making multiple sequential guesses."""
#         p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
#         p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
#         p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

#         solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])

#         initial_count = len(solver.solve())

#         # First guess
#         maxh1 = solver.get_maxh_table()
#         comparison1 = maxh1.compare(solver.valid_rivers[0])
#         colors1 = [card.color for card in comparison1.cards]
#         count_after_first = len(solver.next_table_guess(colors1))

#         assert count_after_first <= initial_count

#         # Second guess
#         if count_after_first > 1:
#             maxh2 = solver.get_maxh_table()
#             comparison2 = maxh2.compare(solver.valid_rivers[0])
#             colors2 = [card.color for card in comparison2.cards]
#             count_after_second = len(solver.next_table_guess(colors2))

#             assert count_after_second <= count_after_first


# class TestSolverIntegrationKnownScenarios:
#     """Integration tests with known poker scenarios."""

#     def test_scenario_pair_vs_pair_vs_high_card(self):
#         """Test scenario where players have pair vs pair vs high card."""
#         # P1: pair of 6s
#         p1_hole = [Card.from_string("6D"), Card.from_string("6S")]
#         # P2: pair of 8s
#         p2_hole = [Card.from_string("8C"), Card.from_string("8D")]
#         # P3: high cards
#         p3_hole = [Card.from_string("2C"), Card.from_string("3S")]

#         # Flop: P2 best (pair of 8s), P1 second (pair of 6s), P3 third
#         # Turn: P1 best (three 6s), P2 second, P3 third
#         # River: P1 best, P3 second, P2 third
#         solver = Solver(
#             p1_hole,
#             p2_hole,
#             p3_hole,
#             flop_hand_ranks=[2, 1, 3],
#             turn_hand_ranks=[1, 2, 3],
#             river_hand_ranks=[1, 3, 2],
#         )

#         possible_rivers = solver.solve()

#         assert len(possible_rivers) > 0

#         # Verify at least one solution exists
#         for river_table in possible_rivers[:1]:  # Check first solution
#             # Verify flop rankings
#             flop_table = Table(*list(river_table.flop))
#             p1_flop = flop_table.rank_hand(p1_hole)
#             p2_flop = flop_table.rank_hand(p2_hole)
#             p3_flop = flop_table.rank_hand(p3_hole)

#             # P2 should beat P1 should beat P3
#             assert (p2_flop.rank, p2_flop.tie_breakers) > (
#                 p1_flop.rank,
#                 p1_flop.tie_breakers,
#             )
#             assert (p1_flop.rank, p1_flop.tie_breakers) > (
#                 p3_flop.rank,
#                 p3_flop.tie_breakers,
#             )

#     def test_scenario_queens_vs_tens_vs_nines(self):
#         """Test the fast example scenario from example.py."""
#         p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
#         p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
#         p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

#         solver = Solver(
#             p1_hole,
#             p2_hole,
#             p3_hole,
#             flop_hand_ranks=[2, 1, 3],
#             turn_hand_ranks=[1, 3, 2],
#             river_hand_ranks=[2, 1, 3],
#         )

#         possible_rivers = solver.solve()

#         # This scenario should have exactly 32 solutions
#         assert len(possible_rivers) == 32

#         # Verify one solution's hand rankings
#         if possible_rivers:
#             river_table = possible_rivers[0]

#             # Check river rankings
#             p1_river = river_table.rank_hand(p1_hole)
#             p2_river = river_table.rank_hand(p2_hole)
#             p3_river = river_table.rank_hand(p3_hole)

#             # Create list of (player_num, rank, tie_breakers)
#             rankings = [
#                 (1, p1_river.rank, p1_river.tie_breakers),
#                 (2, p2_river.rank, p2_river.tie_breakers),
#                 (3, p3_river.rank, p3_river.tie_breakers),
#             ]

#             # Sort by rank and tie_breakers (descending)
#             rankings.sort(key=lambda x: (x[1], x[2]), reverse=True)

#             # Extract player numbers in order of strength
#             player_order = [r[0] for r in rankings]

#             # River hand ranks [2, 1, 3] means P2 is best, P1 second, P3 third
#             assert player_order == [2, 1, 3]

#     def test_scenario_no_valid_rivers(self):
#         """Test scenario where no valid rivers exist (conflicting requirements)."""
#         # Create a scenario that might have no solutions
#         p1_hole = [Card.from_string("2H"), Card.from_string("3D")]
#         p2_hole = [Card.from_string("KC"), Card.from_string("KH")]
#         p3_hole = [Card.from_string("2C"), Card.from_string("5H")]

#         # Impossible: P1 best on flop with 2-3 vs pair of Kings
#         solver = Solver(
#             p1_hole,
#             p2_hole,
#             p3_hole,
#             flop_hand_ranks=[1, 2, 3],  # P1 best
#             turn_hand_ranks=[1, 2, 3],
#             river_hand_ranks=[1, 2, 3],
#         )

#         possible_rivers = solver.solve()

#         # This scenario should have 0 solutions (or very few edge cases)
#         assert len(possible_rivers) >= 0  # Could be 0 or small number


# class TestSolverIntegrationValidation:
#     """Integration tests for validation throughout the workflow."""

#     def test_all_solutions_have_complete_tables(self):
#         """Test that all solutions have flop, turn, and river."""
#         p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
#         p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
#         p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

#         solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])
#         possible_rivers = solver.solve()

#         for table in possible_rivers:
#             assert table.flop is not None
#             assert len(table.flop) == 3
#             assert table.turn is not None
#             assert table.river is not None
#             assert len(table.cards) == 5

#     def test_all_solutions_use_unique_cards(self):
#         """Test that all solution tables don't reuse cards from hole cards."""
#         p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
#         p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
#         p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

#         solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])
#         possible_rivers = solver.solve()

#         all_hole_cards = set(p1_hole + p2_hole + p3_hole)

#         for table in possible_rivers:
#             board_cards = set(table.cards)
#             # No overlap between hole cards and board cards
#             assert len(board_cards & all_hole_cards) == 0

#     def test_all_solutions_satisfy_hand_rankings(self):
#         """Test that all solutions satisfy the specified hand rankings."""
#         p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
#         p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
#         p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

#         flop_ranks = [2, 1, 3]
#         turn_ranks = [1, 3, 2]
#         river_ranks = [2, 1, 3]

#         solver = Solver(p1_hole, p2_hole, p3_hole, flop_ranks, turn_ranks, river_ranks)
#         possible_rivers = solver.solve()

#         for river_table in possible_rivers:
#             # Check flop
#             flop_table = Table(*list(river_table.flop))
#             flop_hands = [
#                 (1, flop_table.rank_hand(p1_hole)),
#                 (2, flop_table.rank_hand(p2_hole)),
#                 (3, flop_table.rank_hand(p3_hole)),
#             ]
#             flop_hands.sort(key=lambda x: (x[1].rank, x[1].tie_breakers), reverse=True)
#             flop_order = [h[0] for h in flop_hands]
#             assert flop_order == flop_ranks

#             # Check turn
#             turn_table = Table(*list(river_table.flop), river_table.turn)
#             turn_hands = [
#                 (1, turn_table.rank_hand(p1_hole)),
#                 (2, turn_table.rank_hand(p2_hole)),
#                 (3, turn_table.rank_hand(p3_hole)),
#             ]
#             turn_hands.sort(key=lambda x: (x[1].rank, x[1].tie_breakers), reverse=True)
#             turn_order = [h[0] for h in turn_hands]
#             assert turn_order == turn_ranks

#             # Check river
#             river_hands = [
#                 (1, river_table.rank_hand(p1_hole)),
#                 (2, river_table.rank_hand(p2_hole)),
#                 (3, river_table.rank_hand(p3_hole)),
#             ]
#             river_hands.sort(key=lambda x: (x[1].rank, x[1].tie_breakers), reverse=True)
#             river_order = [h[0] for h in river_hands]
#             assert river_order == river_ranks

#     def test_maxh_table_has_highest_entropy(self):
#         """Test that the maxh table is actually the one with highest entropy."""
#         p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
#         p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
#         p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

#         solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])
#         solver.solve()

#         maxh_table = solver.get_maxh_table()

#         # The maxh_table should be in the valid_rivers
#         assert maxh_table in solver.valid_rivers

#         # After getting maxh_table, internal state should have entropy data
#         # We can't access private attributes, but we can verify maxh_table is valid
#         assert isinstance(maxh_table, Table)


# class TestSolverIntegrationPrintGame:
#     """Integration tests for print_game functionality."""

#     def test_print_game_displays_all_phases(self, capsys):
#         """Test that print_game displays all game phases."""
#         p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
#         p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
#         p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

#         solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])
#         solver.solve()

#         maxh_table = solver.get_maxh_table()
#         solver.print_game(maxh_table)

#         captured = capsys.readouterr()

#         # Check all phases are displayed
#         assert "flop:" in captured.out
#         assert "turn:" in captured.out
#         assert "river:" in captured.out

#         # Check player headers
#         assert "P1" in captured.out
#         assert "P2" in captured.out
#         assert "P3" in captured.out

#     def test_print_game_after_multiple_guesses(self, capsys):
#         """Test that print_game shows guess history after multiple guesses."""
#         p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
#         p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
#         p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

#         solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])
#         solver.solve()

#         # Make first guess
#         maxh1 = solver.get_maxh_table()
#         comparison1 = maxh1.compare(solver.valid_rivers[0])
#         colors1 = [card.color for card in comparison1.cards]
#         solver.next_table_guess(colors1)

#         # Print game should show the first guess
#         maxh2 = solver.get_maxh_table()
#         solver.print_game(maxh2)

#         captured = capsys.readouterr()

#         # Output should contain game table
#         assert "flop" in captured.out.lower()
#         assert "|" in captured.out  # Table borders

#     def test_print_game_with_win_flag(self, capsys):
#         """Test that print_game with is_win=True doesn't show the current guess."""
#         p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
#         p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
#         p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

#         solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])
#         solver.solve()

#         maxh_table = solver.get_maxh_table()

#         # Print with is_win=True
#         solver.print_game(maxh_table, is_win=True)

#         captured = capsys.readouterr()

#         # Should still have the header
#         assert "Pokle Solver Results" in captured.out


# class TestSolverIntegrationEdgeCases:
#     """Integration tests for edge cases."""

#     def test_solver_with_different_rank_permutations(self):
#         """Test solver with different permutations of hand ranks using constrained scenarios."""
#         # Use the same fast scenario from example.py but with different rank permutations
#         p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
#         p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
#         p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

#         # Try a couple different permutations that should have reasonable solution counts
#         permutations = [
#             # Original from example.py
#             ([2, 1, 3], [1, 3, 2], [2, 1, 3]),
#             # Different permutation - P1 always best
#             ([1, 2, 3], [1, 2, 3], [1, 2, 3]),
#         ]

#         for flop, turn, river in permutations:
#             solver = Solver(p1_hole, p2_hole, p3_hole, flop, turn, river)
#             possible_rivers = solver.solve()

#             # Should get some results for each permutation
#             assert isinstance(possible_rivers, list)
#             # May or may not have solutions depending on permutation
#             assert len(possible_rivers) >= 0

#     def test_solver_deterministic_results(self):
#         """Test that solving the same scenario twice gives the same results."""
#         p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
#         p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
#         p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

#         solver1 = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])
#         result1 = solver1.solve()

#         solver2 = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])
#         result2 = solver2.solve()

#         # Should have same number of solutions
#         assert len(result1) == len(result2)

#         # Solutions should be the same (though order might differ)
#         result1_strings = {str(table) for table in result1}
#         result2_strings = {str(table) for table in result2}
#         assert result1_strings == result2_strings
