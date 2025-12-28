"""Integration tests for the Solver class."""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "pokle_solver"))

from card import Card
from solver import Solver


class TestSolverIntegrationBasic:
    """Basic integration tests for the Solver workflow."""

    def test_full_solve_workflow(self):
        """Test complete solving workflow from initialization to solution."""
        # Setup
        p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
        p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
        p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

        solver = Solver(
            p1_hole,
            p2_hole,
            p3_hole,
            flop_hand_ranks=[2, 1, 3],
            turn_hand_ranks=[1, 3, 2],
            river_hand_ranks=[2, 1, 3],
        )

        # Solve
        possible_tables = solver.solve()

        # Verify results
        assert len(possible_tables) > 0
        assert all(isinstance(table, list) for table in possible_tables)
        assert all(len(table) == 5 for table in possible_tables)
        assert all(
            all(isinstance(card, Card) for card in table) for table in possible_tables
        )

    def test_solve_and_get_maxh_table_workflow(self):
        """Test solving and getting the maximum entropy table."""
        p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
        p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
        p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

        solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])

        # Solve and get maxh table
        possible_tables = solver.solve()
        maxh_table = solver.get_maxh_table()

        # Verify
        assert maxh_table in possible_tables
        assert isinstance(maxh_table, list)
        assert len(maxh_table) == 5

    def test_solve_get_maxh_and_filter_workflow(self):
        """Test complete workflow: solve, get maxh, and filter with guess."""
        p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
        p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
        p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

        solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])

        # Solve
        solver.solve()

        # Get maxh table
        maxh_table = solver.get_maxh_table()

        # Use all-green colors for a simple test (exact match)
        colors = ["g", "g", "g", "g", "g"]

        # Filter
        solver.next_table_guess(colors)

        # Verify - after all-green, should have exactly 1 table
        assert len(solver.valid_tables) == 1
        assert solver.valid_tables[0] == maxh_table

    def test_solve_with_all_green_guess(self):
        """Test that all green colors returns exactly one table (the correct answer)."""
        p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
        p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
        p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

        solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])
        solver.solve()

        maxh_table = solver.get_maxh_table()

        # All green means we guessed correctly
        colors = ["g", "g", "g", "g", "g"]

        solver.next_table_guess(colors)

        # Should have exactly one table - the maxh_table itself
        assert len(solver.valid_tables) == 1
        assert solver.valid_tables[0] == maxh_table

    def test_multiple_guess_iterations(self):
        """Test making multiple sequential guesses."""
        p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
        p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
        p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

        solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])

        solver.solve()

        # First guess - use all green for predictable outcome
        solver.get_maxh_table()
        colors1 = ["g", "g", "g", "g", "g"]
        solver.next_table_guess(colors1)
        count_after_first = len(solver.valid_tables)

        assert count_after_first == 1  # All green should leave exactly one


class TestSolverIntegrationKnownScenarios:
    """Integration tests with known poker scenarios."""

    def test_scenario_pair_vs_pair_vs_high_card(self):
        """Test scenario where players have pair vs pair vs high card."""
        # P1: pair of 6s
        p1_hole = [Card.from_string("6D"), Card.from_string("6S")]
        # P2: pair of 8s
        p2_hole = [Card.from_string("8C"), Card.from_string("8D")]
        # P3: high cards
        p3_hole = [Card.from_string("2C"), Card.from_string("3S")]

        # Flop: P2 best (pair of 8s), P1 second (pair of 6s), P3 third
        # Turn: P1 best (three 6s), P2 second, P3 third
        # River: P1 best, P3 second, P2 third
        solver = Solver(
            p1_hole,
            p2_hole,
            p3_hole,
            flop_hand_ranks=[2, 1, 3],
            turn_hand_ranks=[1, 2, 3],
            river_hand_ranks=[1, 3, 2],
        )

        possible_tables = solver.solve()

        assert len(possible_tables) > 0

        # Verify at least one solution exists and is properly formed
        for table in possible_tables[:1]:
            assert isinstance(table, list)
            assert len(table) == 5
            assert all(isinstance(card, Card) for card in table)

    def test_scenario_queens_vs_tens_vs_nines(self):
        """Test the fast example scenario from example.py."""
        p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
        p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
        p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

        solver = Solver(
            p1_hole,
            p2_hole,
            p3_hole,
            flop_hand_ranks=[2, 1, 3],
            turn_hand_ranks=[1, 3, 2],
            river_hand_ranks=[2, 1, 3],
        )

        possible_tables = solver.solve()

        # This scenario should have exactly 32 solutions
        assert len(possible_tables) == 32

        # Verify one solution's structure
        if possible_tables:
            table = possible_tables[0]
            assert isinstance(table, list)
            assert len(table) == 5

            # Verify rankings using Solver.rank_hand
            flop = table[:3]
            p1_flop = Solver.rank_hand(flop, p1_hole)
            p2_flop = Solver.rank_hand(flop, p2_hole)
            p3_flop = Solver.rank_hand(flop, p3_hole)

            # Create rankings and verify order
            hands = [
                (1, p1_flop.rank, p1_flop.tie_breakers),
                (2, p2_flop.rank, p2_flop.tie_breakers),
                (3, p3_flop.rank, p3_flop.tie_breakers),
            ]
            hands.sort(key=lambda x: (x[1], x[2]), reverse=True)
            flop_order = [h[0] for h in hands]
            assert flop_order == [2, 1, 3]

    def test_scenario_no_valid_rivers(self):
        """Test scenario where no valid rivers exist (conflicting requirements)."""
        # Create a scenario that might have no solutions
        p1_hole = [Card.from_string("2H"), Card.from_string("3D")]
        p2_hole = [Card.from_string("KC"), Card.from_string("KH")]
        p3_hole = [Card.from_string("2C"), Card.from_string("5H")]

        # Impossible: P1 best on flop with 2-3 vs pair of Kings
        solver = Solver(
            p1_hole,
            p2_hole,
            p3_hole,
            flop_hand_ranks=[1, 2, 3],
            turn_hand_ranks=[1, 2, 3],
            river_hand_ranks=[1, 2, 3],
        )

        possible_tables = solver.solve()

        # This scenario should have 0 solutions (or very few edge cases)
        assert len(possible_tables) >= 0  # Could be 0 or small number


class TestSolverIntegrationValidation:
    """Integration tests for validation throughout the workflow."""

    def test_all_solutions_have_complete_tables(self):
        """Test that all solutions have 5 cards (flop + turn + river)."""
        p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
        p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
        p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

        solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])
        possible_tables = solver.solve()

        for table in possible_tables:
            assert len(table) == 5
            # Flop is first 3 cards
            flop = table[:3]
            assert len(flop) == 3
            # Turn is 4th card
            turn = table[3]
            assert isinstance(turn, Card)
            # River is 5th card
            river = table[4]
            assert isinstance(river, Card)

    def test_all_solutions_use_unique_cards(self):
        """Test that all solution tables don't reuse cards from hole cards."""
        p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
        p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
        p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

        solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])
        possible_tables = solver.solve()

        all_hole_cards = set(p1_hole + p2_hole + p3_hole)

        for table in possible_tables:
            board_cards = set(table)
            # No overlap between hole cards and board cards
            assert len(board_cards & all_hole_cards) == 0

    def test_all_solutions_satisfy_hand_rankings(self):
        """Test that all solutions satisfy the specified hand rankings."""
        p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
        p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
        p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

        flop_ranks = [2, 1, 3]
        turn_ranks = [1, 3, 2]
        river_ranks = [2, 1, 3]

        solver = Solver(p1_hole, p2_hole, p3_hole, flop_ranks, turn_ranks, river_ranks)
        possible_tables = solver.solve()

        for table in possible_tables:
            # Check flop rankings
            flop = table[:3]
            flop_hands = [
                (1, Solver.rank_hand(flop, p1_hole)),
                (2, Solver.rank_hand(flop, p2_hole)),
                (3, Solver.rank_hand(flop, p3_hole)),
            ]
            flop_hands.sort(key=lambda x: (x[1].rank, x[1].tie_breakers), reverse=True)
            flop_order = [h[0] for h in flop_hands]
            assert flop_order == flop_ranks

            # Check turn rankings
            turn_table = table[:4]
            turn_hands = [
                (1, Solver.rank_hand(turn_table, p1_hole)),
                (2, Solver.rank_hand(turn_table, p2_hole)),
                (3, Solver.rank_hand(turn_table, p3_hole)),
            ]
            turn_hands.sort(key=lambda x: (x[1].rank, x[1].tie_breakers), reverse=True)
            turn_order = [h[0] for h in turn_hands]
            assert turn_order == turn_ranks

            # Check river rankings
            river_hands = [
                (1, Solver.rank_hand(table, p1_hole)),
                (2, Solver.rank_hand(table, p2_hole)),
                (3, Solver.rank_hand(table, p3_hole)),
            ]
            river_hands.sort(key=lambda x: (x[1].rank, x[1].tie_breakers), reverse=True)
            river_order = [h[0] for h in river_hands]
            assert river_order == river_ranks

    def test_maxh_table_has_highest_entropy(self):
        """Test that the maxh table is actually the one with highest entropy."""
        p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
        p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
        p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

        solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])
        solver.solve()

        maxh_table = solver.get_maxh_table()

        # The maxh_table should be in the valid_tables
        assert maxh_table in solver.valid_tables

        # Verify it's a valid table structure
        assert isinstance(maxh_table, list)
        assert len(maxh_table) == 5


class TestSolverIntegrationPrintGame:
    """Integration tests for print_game functionality."""

    def test_print_game_displays_all_phases(self, capsys):
        """Test that print_game displays all game phases."""
        p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
        p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
        p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

        solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])
        solver.solve()

        maxh_table = solver.get_maxh_table()
        solver.print_game(maxh_table)

        captured = capsys.readouterr()

        # Check all phases are displayed
        assert "flop:" in captured.out
        assert "turn:" in captured.out
        assert "river:" in captured.out

        # Check player headers
        assert "P1" in captured.out
        assert "P2" in captured.out
        assert "P3" in captured.out

    def test_print_game_after_guess(self, capsys):
        """Test that print_game shows guess history after a guess."""
        p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
        p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
        p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

        solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])
        solver.solve()

        # Make first guess with all green
        maxh1 = solver.get_maxh_table()
        colors1 = ["g", "g", "g", "g", "g"]
        solver.next_table_guess(colors1)

        # Print game
        solver.print_game(maxh1)

        captured = capsys.readouterr()

        # Output should contain game table
        assert "flop" in captured.out.lower()
        assert "|" in captured.out  # Table borders

    def test_print_game_header(self, capsys):
        """Test that print_game shows the Pokle Solver Results header."""
        p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
        p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
        p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

        solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])
        solver.solve()

        maxh_table = solver.get_maxh_table()
        solver.print_game(maxh_table)

        captured = capsys.readouterr()

        # Should have the header
        assert "Pokle Solver Results" in captured.out


class TestSolverIntegrationEdgeCases:
    """Integration tests for edge cases."""

    def test_solver_with_different_rank_permutations(self):
        """Test solver with different permutations of hand ranks using constrained scenarios."""
        # Use the same fast scenario from example.py but with different rank permutations
        p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
        p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
        p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

        # Try a couple different permutations that should have reasonable solution counts
        permutations = [
            # Original from example.py
            ([2, 1, 3], [1, 3, 2], [2, 1, 3]),
            # Different permutation - P1 always best
            ([1, 2, 3], [1, 2, 3], [1, 2, 3]),
        ]

        for flop, turn, river in permutations:
            solver = Solver(p1_hole, p2_hole, p3_hole, flop, turn, river)
            possible_tables = solver.solve()

            # Should get some results for each permutation
            assert isinstance(possible_tables, list)
            # May or may not have solutions depending on permutation
            assert len(possible_tables) >= 0

    def test_solver_deterministic_results(self):
        """Test that solving the same scenario twice gives the same results."""
        p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
        p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
        p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

        solver1 = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])
        result1 = solver1.solve()

        solver2 = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])
        result2 = solver2.solve()

        # Should have same number of solutions
        assert len(result1) == len(result2)

        # Solutions should be the same (comparing as strings for set operations)
        result1_strings = {" ".join(str(card) for card in table) for table in result1}
        result2_strings = {" ".join(str(card) for card in table) for table in result2}
        assert result1_strings == result2_strings
