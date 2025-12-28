"""Unit tests for the Solver class."""

import pytest
import sys
import numpy as np
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "pokle_solver"))

from card import Card
from solver import Solver, PhaseEvaluation, MASTER_DECK


class TestSolverInitialization:
    """Test Solver class initialization and validation."""

    def test_init_valid_inputs(self):
        """Test initialization with valid inputs."""
        p1_hole = [Card(10, "H"), Card(11, "H")]
        p2_hole = [Card(2, "C"), Card(3, "C")]
        p3_hole = [Card(14, "D"), Card(13, "D")]

        solver = Solver(p1_hole, p2_hole, p3_hole, [1, 2, 3], [2, 1, 3], [3, 2, 1])

        assert solver.hole_cards["P1"] == p1_hole
        assert solver.hole_cards["P2"] == p2_hole
        assert solver.hole_cards["P3"] == p3_hole
        assert solver.flop_hand_ranks == [1, 2, 3]
        assert solver.turn_hand_ranks == [2, 1, 3]
        assert solver.river_hand_ranks == [3, 2, 1]

    def test_init_invalid_hole_cards_not_list(self):
        """Test that non-list hole cards raise ValueError."""
        with pytest.raises(
            ValueError, match="must be a list of exactly 2 Card objects"
        ):
            Solver(
                (Card(10, "H"), Card(11, "H")),  # type: ignore[arg-type]  # tuple instead of list
                [Card(2, "C"), Card(3, "C")],
                [Card(14, "D"), Card(13, "D")],
                [1, 2, 3],
                [2, 1, 3],
                [3, 2, 1],
            )

    def test_init_invalid_hole_cards_wrong_count(self):
        """Test that hole cards with wrong count raise ValueError."""
        with pytest.raises(
            ValueError, match="must be a list of exactly 2 Card objects"
        ):
            Solver(
                [Card(10, "H")],  # Only 1 card
                [Card(2, "C"), Card(3, "C")],
                [Card(14, "D"), Card(13, "D")],
                [1, 2, 3],
                [2, 1, 3],
                [3, 2, 1],
            )

    def test_init_invalid_hole_cards_not_card_objects(self):
        """Test that non-Card objects in hole cards raise ValueError."""
        with pytest.raises(
            ValueError, match="must be a list of exactly 2 Card objects"
        ):
            Solver(
                [Card(10, "H"), "invalid"],
                [Card(2, "C"), Card(3, "C")],
                [Card(14, "D"), Card(13, "D")],
                [1, 2, 3],
                [2, 1, 3],
                [3, 2, 1],
            )

    def test_init_invalid_hand_ranks_not_list(self):
        """Test that non-list hand ranks raise ValueError."""
        p1_hole = [Card(10, "H"), Card(11, "H")]
        p2_hole = [Card(2, "C"), Card(3, "C")]
        p3_hole = [Card(14, "D"), Card(13, "D")]

        with pytest.raises(ValueError, match="must be a permutation of"):
            Solver(p1_hole, p2_hole, p3_hole, (1, 2, 3), [2, 1, 3], [3, 2, 1])  # type: ignore[arg-type]

    def test_init_invalid_hand_ranks_wrong_values(self):
        """Test that hand ranks with wrong values raise ValueError."""
        p1_hole = [Card(10, "H"), Card(11, "H")]
        p2_hole = [Card(2, "C"), Card(3, "C")]
        p3_hole = [Card(14, "D"), Card(13, "D")]

        with pytest.raises(ValueError, match="must be a permutation of"):
            Solver(p1_hole, p2_hole, p3_hole, [1, 2, 4], [2, 1, 3], [3, 2, 1])

    def test_init_invalid_hand_ranks_duplicates(self):
        """Test that hand ranks with duplicates raise ValueError."""
        p1_hole = [Card(10, "H"), Card(11, "H")]
        p2_hole = [Card(2, "C"), Card(3, "C")]
        p3_hole = [Card(14, "D"), Card(13, "D")]

        with pytest.raises(ValueError, match="must be a permutation of"):
            Solver(p1_hole, p2_hole, p3_hole, [1, 1, 2], [2, 1, 3], [3, 2, 1])

    def test_valid_tables_property_initially_empty(self):
        """Test that valid_tables property starts empty."""
        p1_hole = [Card(10, "H"), Card(11, "H")]
        p2_hole = [Card(2, "C"), Card(3, "C")]
        p3_hole = [Card(14, "D"), Card(13, "D")]

        solver = Solver(p1_hole, p2_hole, p3_hole, [1, 2, 3], [2, 1, 3], [3, 2, 1])

        assert solver.valid_tables == []
        assert isinstance(solver.valid_tables, list)

    def test_valid_tables_property_is_read_only(self):
        """Test that valid_tables property cannot be set directly."""
        p1_hole = [Card(10, "H"), Card(11, "H")]
        p2_hole = [Card(2, "C"), Card(3, "C")]
        p3_hole = [Card(14, "D"), Card(13, "D")]

        solver = Solver(p1_hole, p2_hole, p3_hole, [1, 2, 3], [2, 1, 3], [3, 2, 1])

        with pytest.raises(AttributeError):
            solver.valid_tables = []  # type: ignore[misc]


class TestSolverPrivateMethods:
    """Test that private methods are not accessible."""

    def test_possible_flops_is_private(self):
        """Test that possible_flops is not accessible."""
        p1_hole = [Card(10, "H"), Card(11, "H")]
        p2_hole = [Card(2, "C"), Card(3, "C")]
        p3_hole = [Card(14, "D"), Card(13, "D")]

        solver = Solver(p1_hole, p2_hole, p3_hole, [1, 2, 3], [2, 1, 3], [3, 2, 1])

        with pytest.raises(AttributeError):
            solver.possible_flops()  # type: ignore[attr-defined]

    def test_possible_turns_is_private(self):
        """Test that possible_turns is not accessible."""
        p1_hole = [Card(10, "H"), Card(11, "H")]
        p2_hole = [Card(2, "C"), Card(3, "C")]
        p3_hole = [Card(14, "D"), Card(13, "D")]

        solver = Solver(p1_hole, p2_hole, p3_hole, [1, 2, 3], [2, 1, 3], [3, 2, 1])

        with pytest.raises(AttributeError):
            solver.possible_turns([])  # type: ignore[attr-defined]

    def test_possible_rivers_is_private(self):
        """Test that possible_rivers is not accessible."""
        p1_hole = [Card(10, "H"), Card(11, "H")]
        p2_hole = [Card(2, "C"), Card(3, "C")]
        p3_hole = [Card(14, "D"), Card(13, "D")]

        solver = Solver(p1_hole, p2_hole, p3_hole, [1, 2, 3], [2, 1, 3], [3, 2, 1])

        with pytest.raises(AttributeError):
            solver.possible_rivers([])  # type: ignore[attr-defined]

    def test_compare_tables_is_private(self):
        """Test that compare_tables is not accessible."""
        p1_hole = [Card(10, "H"), Card(11, "H")]
        p2_hole = [Card(2, "C"), Card(3, "C")]
        p3_hole = [Card(14, "D"), Card(13, "D")]

        solver = Solver(p1_hole, p2_hole, p3_hole, [1, 2, 3], [2, 1, 3], [3, 2, 1])

        with pytest.raises(AttributeError):
            solver.compare_tables([], [])  # type: ignore[attr-defined]


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
        # Each table is a list of 5 Card objects
        assert all(isinstance(table, list) for table in result)
        assert all(len(table) == 5 for table in result)
        assert all(all(isinstance(card, Card) for card in table) for table in result)

    def test_solve_updates_valid_tables_property(self):
        """Test that solve updates the valid_tables property."""
        p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
        p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
        p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

        solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])

        assert len(solver.valid_tables) == 0

        result = solver.solve()

        assert len(solver.valid_tables) > 0
        assert solver.valid_tables == result

    def test_get_maxh_table_before_solve_raises_error(self):
        """Test that get_maxh_table raises error if called before solve."""
        p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
        p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
        p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

        solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])

        with pytest.raises(ValueError, match="No possible rivers calculated"):
            solver.get_maxh_table()

    def test_get_maxh_table_returns_list(self):
        """Test that get_maxh_table returns a list of Card objects."""
        p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
        p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
        p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

        solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])
        solver.solve()

        maxh_table = solver.get_maxh_table()

        assert isinstance(maxh_table, list)
        assert len(maxh_table) == 5
        assert all(isinstance(card, Card) for card in maxh_table)

    def test_get_maxh_table_returns_valid_table(self):
        """Test that get_maxh_table returns a table from valid_tables."""
        p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
        p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
        p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

        solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])
        solver.solve()

        maxh_table = solver.get_maxh_table()

        # The maxh_table should be in valid_tables
        assert maxh_table in solver.valid_tables

    def test_next_table_guess_before_solve_raises_error(self):
        """Test that next_table_guess raises error if called before solve."""
        p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
        p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
        p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

        solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])

        with pytest.raises(ValueError, match="No current guess available"):
            solver.next_table_guess(["g", "g", "g", "g", "g"])

    def test_next_table_guess_invalid_color_count(self):
        """Test that next_table_guess validates color count."""
        p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
        p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
        p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

        solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])
        solver.solve()
        solver.get_maxh_table()

        with pytest.raises(ValueError, match="must be a list of 5 colors"):
            solver.next_table_guess(["g", "g", "g"])

    def test_next_table_guess_invalid_color_values(self):
        """Test that next_table_guess validates color values."""
        p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
        p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
        p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

        solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])
        solver.solve()
        solver.get_maxh_table()

        # Invalid color value should raise KeyError when converting to int
        with pytest.raises(KeyError):
            solver.next_table_guess(["g", "g", "invalid", "g", "g"])

    def test_next_table_guess_filters_valid_tables(self):
        """Test that next_table_guess correctly filters valid_tables with all-green scenario."""
        p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
        p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
        p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

        solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])
        initial_count = len(solver.solve())

        assert initial_count > 0, "Should have at least one valid table"

        maxh_table = solver.get_maxh_table()

        # Test with all-green colors (perfect match scenario)
        # This should leave exactly one table - the maxh_table itself
        all_green = ["g", "g", "g", "g", "g"]
        solver.next_table_guess(all_green)

        assert len(solver.valid_tables) == 1, "All green should match exactly one table"
        assert solver.valid_tables[0] == maxh_table, (
            "All green should return the guess itself"
        )

    def test_print_game_before_solve_raises_error(self):
        """Test that print_game raises error if called before solve."""
        p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
        p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
        p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

        solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])

        table = [Card(2, "H"), Card(3, "H"), Card(4, "H"), Card(5, "H"), Card(6, "H")]

        with pytest.raises(ValueError, match="No possible rivers calculated"):
            solver.print_game(table)

    def test_print_game_invalid_table_type(self):
        """Test that print_game validates table is a list of 5 Card objects."""
        p1_hole = [Card.from_string("QD"), Card.from_string("QC")]
        p2_hole = [Card.from_string("10H"), Card.from_string("2H")]
        p3_hole = [Card.from_string("9H"), Card.from_string("KH")]

        solver = Solver(p1_hole, p2_hole, p3_hole, [2, 1, 3], [1, 3, 2], [2, 1, 3])
        solver.solve()

        with pytest.raises(ValueError, match="must be a list of 5 Card objects"):
            solver.print_game("not a table")  # type: ignore[arg-type]

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
        table = [Card(2, "H"), Card(3, "H"), Card(4, "H")]
        phase_eval = PhaseEvaluation(table=table, expected_rankings=[1, 2, 3])

        assert phase_eval.table == table
        assert phase_eval.expected_rankings == [1, 2, 3]
        assert phase_eval.prev_cards_used is None
        assert phase_eval.validate_all_cards_used is False

    def test_phase_evaluation_with_all_fields(self):
        """Test creating a PhaseEvaluation with all fields."""
        table = [Card(2, "H"), Card(3, "H"), Card(4, "H"), Card(5, "H")]
        cards_used = {Card(2, "H"), Card(3, "H")}

        phase_eval = PhaseEvaluation(
            table=table,
            expected_rankings=[2, 1, 3],
            prev_cards_used=cards_used,
            validate_all_cards_used=True,
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
        for suit in ["H", "D", "C", "S"]:
            assert suits.count(suit) == 13  # 13 ranks per suit


class TestCompareTablesMethod:
    """Unit tests for the Solver.__compare_tables method.

    The compare_tables method compares a guess table against answer tables and
    returns a 5-digit integer encoding the color result for each card position:
    - 2 = green (exact match)
    - 1 = yellow (rank or suit match, but not both)
    - 0 = grey (no match)

    For the flop (first 3 cards), order doesn't matter - a card matches if it
    matches ANY card in the answer's flop. For turn (4th) and river (5th),
    comparison is positional.

    These test cases are taken from the README documentation.
    """

    def test_compare_tables_example_1(self):
        """Test: guess=[4S, KD, 7S, 4D, 6S] vs answer=[3H, 9D, KS, 6C, 4S]

        Expected result: 11101
        - 4S in flop: 4 not in [3,9,13], S in [H,D,S] -> yellow (1)
        - KD in flop: K(13) matches KS rank -> yellow (1)
        - 7S in flop: 7 not in ranks, S in suits -> yellow (1)
        - 4D at turn: 4!=6, D!=C -> grey (0)
        - 6S at river: 6!=4, S==S -> yellow (1)
        """
        guess = [Card.from_string(c) for c in ["4S", "KD", "7S", "4D", "6S"]]
        answer = [Card.from_string(c) for c in ["3H", "9D", "KS", "6C", "4S"]]
        guess_index = np.array([[card.card_index for card in guess]], dtype=np.int8)
        answer_index = np.array([[card.card_index for card in answer]], dtype=np.int8)

        result = np.zeros(1, dtype=np.int16)
        Solver._Solver__compare_tables(guess_index, answer_index, result)  # type: ignore[attr-defined]

        assert result[0] == 11101

    def test_compare_tables_example_2(self):
        """Test: guess=[6D, 7D, 9C, KC, AS] vs answer=[9H, 3S, 6D, KC, 9S]

        Expected result: 20121
        - 6D in flop: exact match with 6D -> green (2)
        - 7D in flop: 7 not in ranks, D used by green match -> grey (0)
        - 9C in flop: 9 matches 9H rank -> yellow (1)
        - KC at turn: exact match -> green (2)
        - AS at river: A!=9, S==S -> yellow (1)
        """
        guess = [Card.from_string(c) for c in ["6D", "7D", "9C", "KC", "AS"]]
        answer = [Card.from_string(c) for c in ["9H", "3S", "6D", "KC", "9S"]]
        guess_index = np.array([[card.card_index for card in guess]], dtype=np.int8)
        answer_index = np.array([[card.card_index for card in answer]], dtype=np.int8)

        result = np.zeros(1, dtype=np.int16)
        Solver._Solver__compare_tables(guess_index, answer_index, result)  # type: ignore[attr-defined]

        assert result[0] == 20121

    def test_compare_tables_example_3(self):
        """Test: guess=[KS, 9S, AS, 4H, 6S] vs answer=[7S, KS, AH, 4C, 6S]

        Expected result: 21112
        - KS in flop: exact match with KS -> green (2)
        - 9S in flop: 9 not in [7,-,14], S in remaining suits -> yellow (1)
        - AS in flop: A(14) matches AH rank -> yellow (1)
        - 4H at turn: 4==4 -> yellow (1)
        - 6S at river: exact match -> green (2)
        """
        guess = [Card.from_string(c) for c in ["KS", "9S", "AS", "4H", "6S"]]
        answer = [Card.from_string(c) for c in ["7S", "KS", "AH", "4C", "6S"]]
        guess_index = np.array([[card.card_index for card in guess]], dtype=np.int8)
        answer_index = np.array([[card.card_index for card in answer]], dtype=np.int8)

        result = np.zeros(1, dtype=np.int16)
        Solver._Solver__compare_tables(guess_index, answer_index, result)  # type: ignore[attr-defined]

        assert result[0] == 21112

    def test_compare_tables_example_4(self):
        """Test: guess=[AS, KS, QS, JH, 10D] vs answer=[AS, 2D, 3C, JD, 10D]

        Expected result: 20012
        - AS in flop: exact match -> green (2)
        - KS in flop: K(13) not in [-,2,3], S not in remaining suits -> grey (0)
        - QS in flop: Q(12) not in remaining ranks -> grey (0)
        - JH at turn: J==J -> yellow (1)
        - 10D at river: exact match -> green (2)
        """
        guess = [Card.from_string(c) for c in ["AS", "KS", "QS", "JH", "10D"]]
        answer = [Card.from_string(c) for c in ["AS", "2D", "3C", "JD", "10D"]]
        guess_index = np.array([[card.card_index for card in guess]], dtype=np.int8)
        answer_index = np.array([[card.card_index for card in answer]], dtype=np.int8)

        result = np.zeros(1, dtype=np.int16)
        Solver._Solver__compare_tables(guess_index, answer_index, result)  # type: ignore[attr-defined]

        assert result[0] == 20012

    def test_compare_tables_example_5(self):
        """Test: guess=[7H, 9S, 7S, 3D, KH] vs answer=[7S, 9S, 7H, 3H, KD]

        Expected result: 22211
        - 7H in flop: exact match with 7H -> green (2)
        - 9S in flop: exact match with 9S -> green (2)
        - 7S in flop: exact match with 7S -> green (2)
        - 3D at turn: 3==3, D!=H -> yellow (1)
        - KH at river: K==K, H!=D -> yellow (1)
        """
        guess = [Card.from_string(c) for c in ["7H", "9S", "7S", "3D", "KH"]]
        answer = [Card.from_string(c) for c in ["7S", "9S", "7H", "3H", "KD"]]
        guess_index = np.array([[card.card_index for card in guess]], dtype=np.int8)
        answer_index = np.array([[card.card_index for card in answer]], dtype=np.int8)

        result = np.zeros(1, dtype=np.int16)
        Solver._Solver__compare_tables(guess_index, answer_index, result)  # type: ignore[attr-defined]

        assert result[0] == 22211

    def test_compare_tables_example_6(self):
        """Test: guess=[JD, JC, KD, 2H, 3S] vs answer=[JD, KS, QH, 2D, 3S]

        Expected result: 20112
        - JD in flop: exact match -> green (2)
        - JC in flop: J not in remaining ranks, C not in remaining suits -> grey (0)
        - KD in flop: K(13) matches KS rank -> yellow (1)
        - 2H at turn: 2==2 -> yellow (1)
        - 3S at river: exact match -> green (2)
        """
        guess = [Card.from_string(c) for c in ["JD", "JC", "KD", "2H", "3S"]]
        answer = [Card.from_string(c) for c in ["JD", "KS", "QH", "2D", "3S"]]
        guess_index = np.array([[card.card_index for card in guess]], dtype=np.int8)
        answer_index = np.array([[card.card_index for card in answer]], dtype=np.int8)

        result = np.zeros(1, dtype=np.int16)
        Solver._Solver__compare_tables(guess_index, answer_index, result)  # type: ignore[attr-defined]

        assert result[0] == 20112

    def test_compare_tables_batch_processing(self):
        """Test that compare_tables correctly handles batch processing of multiple tables."""
        # Create 3 tables as guesses against 3 answers
        guess1 = [Card.from_string(c) for c in ["4S", "KD", "7S", "4D", "6S"]]
        guess2 = [Card.from_string(c) for c in ["6D", "7D", "9C", "KC", "AS"]]
        guess3 = [Card.from_string(c) for c in ["JD", "JC", "KD", "2H", "3S"]]

        answer1 = [Card.from_string(c) for c in ["3H", "9D", "KS", "6C", "4S"]]
        answer2 = [Card.from_string(c) for c in ["9H", "3S", "6D", "KC", "9S"]]
        answer3 = [Card.from_string(c) for c in ["JD", "KS", "QH", "2D", "3S"]]

        guess_indices = np.array(
            [
                [card.card_index for card in guess1],
                [card.card_index for card in guess2],
                [card.card_index for card in guess3],
            ],
            dtype=np.int8,
        )

        answer_indices = np.array(
            [
                [card.card_index for card in answer1],
                [card.card_index for card in answer2],
                [card.card_index for card in answer3],
            ],
            dtype=np.int8,
        )

        result = np.zeros(3, dtype=np.int16)
        Solver._Solver__compare_tables(guess_indices, answer_indices, result)  # type: ignore[attr-defined]

        assert result[0] == 11101
        assert result[1] == 20121
        assert result[2] == 20112

    def test_compare_tables_all_green(self):
        """Test that identical tables return all green (22222)."""
        table = [Card.from_string(c) for c in ["AS", "KS", "QS", "JH", "10D"]]
        table_index = np.array([[card.card_index for card in table]], dtype=np.int8)

        result = np.zeros(1, dtype=np.int16)
        Solver._Solver__compare_tables(table_index, table_index, result)  # type: ignore[attr-defined]

        assert result[0] == 22222

    def test_compare_tables_all_grey(self):
        """Test that completely non-matching tables return all grey (00000)."""
        guess = [Card.from_string(c) for c in ["2H", "3H", "4H", "5H", "6H"]]
        answer = [Card.from_string(c) for c in ["7S", "8S", "9S", "JS", "QS"]]
        guess_index = np.array([[card.card_index for card in guess]], dtype=np.int8)
        answer_index = np.array([[card.card_index for card in answer]], dtype=np.int8)

        result = np.zeros(1, dtype=np.int16)
        Solver._Solver__compare_tables(guess_index, answer_index, result)  # type: ignore[attr-defined]

        assert result[0] == 0  # 00000
