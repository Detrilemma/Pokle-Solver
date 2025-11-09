"""Unit tests for the Solver class."""
import pytest
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from card import Card
from solver import Solver, PhaseEvaluation, MASTER_DECK
from table import Table
import pandas as pd


class TestSolverInitialization:
    """Test Solver class initialization and validation."""

    def test_init_valid_inputs(self):
        """Test initialization with valid inputs."""
        p1_hole = [Card(10, 'H'), Card(11, 'H')]
        p2_hole = [Card(2, 'C'), Card(3, 'C')]
        p3_hole = [Card(14, 'D'), Card(13, 'D')]
        
        solver = Solver(p1_hole, p2_hole, p3_hole, [1, 2, 3], [2, 1, 3], [3, 2, 1])
        
        assert solver.hole_cards["P1"] == p1_hole
        assert solver.hole_cards["P2"] == p2_hole
        assert solver.hole_cards["P3"] == p3_hole
        assert solver.flop_hand_ranks == [1, 2, 3]
        assert solver.turn_hand_ranks == [2, 1, 3]
        assert solver.river_hand_ranks == [3, 2, 1]

    def test_init_invalid_hole_cards_not_list(self):
        """Test that non-list hole cards raise ValueError."""
        with pytest.raises(ValueError, match="must be a list of exactly 2 Card objects"):
            Solver(
                (Card(10, 'H'), Card(11, 'H')),  # tuple instead of list
                [Card(2, 'C'), Card(3, 'C')],
                [Card(14, 'D'), Card(13, 'D')],
                [1, 2, 3], [2, 1, 3], [3, 2, 1]
            )

    def test_init_invalid_hole_cards_wrong_count(self):
        """Test that hole cards with wrong count raise ValueError."""
        with pytest.raises(ValueError, match="must be a list of exactly 2 Card objects"):
            Solver(
                [Card(10, 'H')],  # Only 1 card
                [Card(2, 'C'), Card(3, 'C')],
                [Card(14, 'D'), Card(13, 'D')],
                [1, 2, 3], [2, 1, 3], [3, 2, 1]
            )

    def test_init_invalid_hole_cards_not_card_objects(self):
        """Test that non-Card objects in hole cards raise ValueError."""
        with pytest.raises(ValueError, match="must be a list of exactly 2 Card objects"):
            Solver(
                [Card(10, 'H'), "invalid"],
                [Card(2, 'C'), Card(3, 'C')],
                [Card(14, 'D'), Card(13, 'D')],
                [1, 2, 3], [2, 1, 3], [3, 2, 1]
            )

    def test_init_invalid_hand_ranks_not_list(self):
        """Test that non-list hand ranks raise ValueError."""
        p1_hole = [Card(10, 'H'), Card(11, 'H')]
        p2_hole = [Card(2, 'C'), Card(3, 'C')]
        p3_hole = [Card(14, 'D'), Card(13, 'D')]
        
        with pytest.raises(ValueError, match="must be a permutation of"):
            Solver(p1_hole, p2_hole, p3_hole, (1, 2, 3), [2, 1, 3], [3, 2, 1])

    def test_init_invalid_hand_ranks_wrong_values(self):
        """Test that hand ranks with wrong values raise ValueError."""
        p1_hole = [Card(10, 'H'), Card(11, 'H')]
        p2_hole = [Card(2, 'C'), Card(3, 'C')]
        p3_hole = [Card(14, 'D'), Card(13, 'D')]
        
        with pytest.raises(ValueError, match="must be a permutation of"):
            Solver(p1_hole, p2_hole, p3_hole, [1, 2, 4], [2, 1, 3], [3, 2, 1])

    def test_init_invalid_hand_ranks_duplicates(self):
        """Test that hand ranks with duplicates raise ValueError."""
        p1_hole = [Card(10, 'H'), Card(11, 'H')]
        p2_hole = [Card(2, 'C'), Card(3, 'C')]
        p3_hole = [Card(14, 'D'), Card(13, 'D')]
        
        with pytest.raises(ValueError, match="must be a permutation of"):
            Solver(p1_hole, p2_hole, p3_hole, [1, 1, 2], [2, 1, 3], [3, 2, 1])

    def test_valid_rivers_property_initially_empty(self):
        """Test that valid_rivers property starts empty."""
        p1_hole = [Card(10, 'H'), Card(11, 'H')]
        p2_hole = [Card(2, 'C'), Card(3, 'C')]
        p3_hole = [Card(14, 'D'), Card(13, 'D')]
        
        solver = Solver(p1_hole, p2_hole, p3_hole, [1, 2, 3], [2, 1, 3], [3, 2, 1])
        
        assert solver.valid_rivers == []
        assert isinstance(solver.valid_rivers, list)

    def test_valid_rivers_property_is_read_only(self):
        """Test that valid_rivers property cannot be set directly."""
        p1_hole = [Card(10, 'H'), Card(11, 'H')]
        p2_hole = [Card(2, 'C'), Card(3, 'C')]
        p3_hole = [Card(14, 'D'), Card(13, 'D')]
        
        solver = Solver(p1_hole, p2_hole, p3_hole, [1, 2, 3], [2, 1, 3], [3, 2, 1])
        
        with pytest.raises(AttributeError):
            solver.valid_rivers = []


class TestSolverPrivateMethods:
    """Test that private methods are not accessible."""

    def test_possible_flops_is_private(self):
        """Test that possible_flops is not accessible."""
        p1_hole = [Card(10, 'H'), Card(11, 'H')]
        p2_hole = [Card(2, 'C'), Card(3, 'C')]
        p3_hole = [Card(14, 'D'), Card(13, 'D')]
        
        solver = Solver(p1_hole, p2_hole, p3_hole, [1, 2, 3], [2, 1, 3], [3, 2, 1])
        
        with pytest.raises(AttributeError):
            solver.possible_flops()

    def test_possible_turns_is_private(self):
        """Test that possible_turns is not accessible."""
        p1_hole = [Card(10, 'H'), Card(11, 'H')]
        p2_hole = [Card(2, 'C'), Card(3, 'C')]
        p3_hole = [Card(14, 'D'), Card(13, 'D')]
        
        solver = Solver(p1_hole, p2_hole, p3_hole, [1, 2, 3], [2, 1, 3], [3, 2, 1])
        
        with pytest.raises(AttributeError):
            solver.possible_turns([])

    def test_possible_rivers_is_private(self):
        """Test that possible_rivers is not accessible."""
        p1_hole = [Card(10, 'H'), Card(11, 'H')]
        p2_hole = [Card(2, 'C'), Card(3, 'C')]
        p3_hole = [Card(14, 'D'), Card(13, 'D')]
        
        solver = Solver(p1_hole, p2_hole, p3_hole, [1, 2, 3], [2, 1, 3], [3, 2, 1])
        
        with pytest.raises(AttributeError):
            solver.possible_rivers([])

    def test_entropy_from_series_is_private(self):
        """Test that entropy_from_series is not accessible."""
        p1_hole = [Card(10, 'H'), Card(11, 'H')]
        p2_hole = [Card(2, 'C'), Card(3, 'C')]
        p3_hole = [Card(14, 'D'), Card(13, 'D')]
        
        solver = Solver(p1_hole, p2_hole, p3_hole, [1, 2, 3], [2, 1, 3], [3, 2, 1])
        
        with pytest.raises(AttributeError):
            solver.entropy_from_series(pd.Series([1, 2, 3]))


class TestSolverPublicMethods:
    """Test Solver public methods."""

    def test_solve_returns_list(self):
        """Test that solve returns a list."""
        p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
        p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
        p3_hole = [Card.from_string("9H"), Card.from_string("KH")]
        
        solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])
        result = solver.solve()
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(table, Table) for table in result)

    def test_solve_updates_valid_rivers_property(self):
        """Test that solve updates the valid_rivers property."""
        p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
        p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
        p3_hole = [Card.from_string("9H"), Card.from_string("KH")]
        
        solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])
        
        assert len(solver.valid_rivers) == 0
        
        result = solver.solve()
        
        assert len(solver.valid_rivers) > 0
        assert solver.valid_rivers == result

    def test_get_maxh_table_before_solve_raises_error(self):
        """Test that get_maxh_table raises error if called before solve."""
        p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
        p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
        p3_hole = [Card.from_string("9H"), Card.from_string("KH")]
        
        solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])
        
        with pytest.raises(ValueError, match="No possible rivers calculated"):
            solver.get_maxh_table()

    def test_get_maxh_table_returns_table(self):
        """Test that get_maxh_table returns a Table object."""
        p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
        p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
        p3_hole = [Card.from_string("9H"), Card.from_string("KH")]
        
        solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])
        solver.solve()
        
        maxh_table = solver.get_maxh_table()
        
        assert isinstance(maxh_table, Table)
        assert maxh_table.flop is not None
        assert maxh_table.turn is not None
        assert maxh_table.river is not None

    def test_get_maxh_table_returns_valid_table(self):
        """Test that get_maxh_table returns a table from valid_rivers."""
        p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
        p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
        p3_hole = [Card.from_string("9H"), Card.from_string("KH")]
        
        solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])
        solver.solve()
        
        maxh_table = solver.get_maxh_table()
        
        assert maxh_table in solver.valid_rivers

    def test_next_table_guess_before_solve_raises_error(self):
        """Test that next_table_guess raises error if called before solve."""
        p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
        p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
        p3_hole = [Card.from_string("9H"), Card.from_string("KH")]
        
        solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])
        
        with pytest.raises(ValueError, match="No possible rivers calculated"):
            solver.next_table_guess(['g', 'g', 'g', 'g', 'g'])

    def test_next_table_guess_invalid_color_count(self):
        """Test that next_table_guess validates color count."""
        p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
        p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
        p3_hole = [Card.from_string("9H"), Card.from_string("KH")]
        
        solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])
        solver.solve()
        maxh_table = solver.get_maxh_table()
        
        with pytest.raises(ValueError, match="must be a list of 5 colors"):
            solver.next_table_guess(['g', 'g', 'g'], current_guess=maxh_table)

    def test_next_table_guess_invalid_color_values(self):
        """Test that next_table_guess validates color values."""
        p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
        p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
        p3_hole = [Card.from_string("9H"), Card.from_string("KH")]
        
        solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])
        solver.solve()
        
        # Note: update_colors will validate, but let's check the list validation
        with pytest.raises(ValueError):
            solver.next_table_guess(['g', 'g', 'invalid', 'g', 'g'])

    def test_next_table_guess_filters_valid_rivers(self):
        """Test that next_table_guess correctly filters valid_rivers."""
        p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
        p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
        p3_hole = [Card.from_string("9H"), Card.from_string("KH")]
        
        solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])
        initial_count = len(solver.solve())
        
        maxh_table = solver.get_maxh_table()
        # Pick a different river to compare against
        comparison_river = solver.valid_rivers[-1] if len(solver.valid_rivers) > 1 else solver.valid_rivers[0]
        comparison = maxh_table.compare(comparison_river)
        colors = [card.color for card in comparison.cards]
        
        # Only test if we have a valid comparison (not all colors are the same edge case)
        if not all(c == colors[0] for c in colors):
            result = solver.next_table_guess(colors)
            
            assert isinstance(result, list)
            assert len(result) <= initial_count
            assert all(isinstance(table, Table) for table in result)

    def test_print_game_before_solve_raises_error(self):
        """Test that print_game raises error if called before solve."""
        p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
        p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
        p3_hole = [Card.from_string("9H"), Card.from_string("KH")]
        
        solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])
        
        table = Table(Card(2, 'H'), Card(3, 'H'), Card(4, 'H'), Card(5, 'H'), Card(6, 'H'))
        
        with pytest.raises(ValueError, match="No possible rivers calculated"):
            solver.print_game(table)

    def test_print_game_invalid_table_type(self):
        """Test that print_game validates table type."""
        p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
        p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
        p3_hole = [Card.from_string("9H"), Card.from_string("KH")]
        
        solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])
        solver.solve()
        
        with pytest.raises(ValueError, match="must be an instance of the Table class"):
            solver.print_game("not a table")

    def test_print_game_table_not_in_valid_rivers(self):
        """Test that print_game validates table is in valid_rivers."""
        p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
        p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
        p3_hole = [Card.from_string("9H"), Card.from_string("KH")]
        
        solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])
        solver.solve()
        
        # Create a table that's definitely not in the results
        invalid_table = Table(Card(2, 'H'), Card(3, 'H'), Card(4, 'H'), Card(5, 'H'), Card(6, 'H'))
        
        with pytest.raises(ValueError, match="not in the list of possible rivers"):
            solver.print_game(invalid_table)

    def test_print_game_produces_output(self, capsys):
        """Test that print_game produces console output."""
        p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
        p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
        p3_hole = [Card.from_string("9H"), Card.from_string("KH")]
        
        solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])
        solver.solve()
        
        maxh_table = solver.get_maxh_table()
        solver.print_game(maxh_table)
        
        captured = capsys.readouterr()
        assert "Pokle Solver Results" in captured.out
        assert "P1" in captured.out
        assert "P2" in captured.out
        assert "P3" in captured.out
        assert "flop:" in captured.out
        assert "turn:" in captured.out
        assert "river:" in captured.out


class TestPhaseEvaluationDataclass:
    """Test PhaseEvaluation dataclass."""

    def test_phase_evaluation_creation(self):
        """Test creating a PhaseEvaluation instance."""
        table = Table(Card(2, 'H'), Card(3, 'H'), Card(4, 'H'))
        phase_eval = PhaseEvaluation(
            table=table,
            expected_rankings=[1, 2, 3]
        )
        
        assert phase_eval.table == table
        assert phase_eval.expected_rankings == [1, 2, 3]
        assert phase_eval.prev_cards_used is None
        assert phase_eval.validate_all_cards_used is False

    def test_phase_evaluation_with_all_fields(self):
        """Test creating a PhaseEvaluation with all fields."""
        table = Table(Card(2, 'H'), Card(3, 'H'), Card(4, 'H'), Card(5, 'H'))
        cards_used = {Card(2, 'H'), Card(3, 'H')}
        
        phase_eval = PhaseEvaluation(
            table=table,
            expected_rankings=[2, 1, 3],
            prev_cards_used=cards_used,
            validate_all_cards_used=True
        )
        
        assert phase_eval.table == table
        assert phase_eval.expected_rankings == [2, 1, 3]
        assert phase_eval.prev_cards_used == cards_used
        assert phase_eval.validate_all_cards_used is True


class TestMasterDeck:
    """Test MASTER_DECK constant."""

    def test_master_deck_has_52_cards(self):
        """Test that MASTER_DECK has exactly 52 cards."""
        assert len(MASTER_DECK) == 52

    def test_master_deck_all_cards_unique(self):
        """Test that all cards in MASTER_DECK are unique."""
        card_strings = [str(card) for card in MASTER_DECK]
        assert len(card_strings) == len(set(card_strings))

    def test_master_deck_has_all_ranks(self):
        """Test that MASTER_DECK has all ranks from 2 to 14."""
        ranks = [card.rank for card in MASTER_DECK]
        for rank in range(2, 15):
            assert ranks.count(rank) == 4  # 4 suits per rank

    def test_master_deck_has_all_suits(self):
        """Test that MASTER_DECK has all four suits."""
        suits = [card.suit for card in MASTER_DECK]
        for suit in ['H', 'D', 'C', 'S']:
            assert suits.count(suit) == 13  # 13 ranks per suit
