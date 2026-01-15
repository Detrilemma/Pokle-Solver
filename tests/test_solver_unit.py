"""Unit tests for the Solver class."""

import pytest
import numpy as np

from pokle_solver.card import Card  # type: ignore
from pokle_solver.solver import Solver, PhaseEvaluation, MASTER_DECK  # type: ignore


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

    def test_compare_tables_green_match_priority_over_yellow(self):
        """Test that green matches are found before yellow matches consume the card.

        Regression test for bug where flop cards were processed sequentially,
        allowing an earlier card to "steal" a suit match (yellow) before a later
        card could claim its exact match (green).

        Test case:
        - guess=[4C, 9H, 2C, AD, 3D] (4C at position 0 shares suit with 2C)
        - answer=[2C, 9S, 2S, 4S, 5S] (2C is in the answer's flop)

        Without the fix (processing in order 0->1->2):
        - Position 0 (4C): suit C matches 2C in answer -> yellow (WRONG - steals match)
        - Position 2 (2C): 2C is in answer flop -> green, but answer's 2C already "used"

        With the fix (green pass first, then yellow pass):
        - First pass: 2C at position 2 matches answer's 2C -> green
        - Second pass: 4C at position 0, suit C already claimed by green match -> grey

        Expected: [grey, yellow, green, grey, grey] = 01200
        - 4C: grey (suit C was claimed by 2C's green match)
        - 9H: yellow (rank 9 matches 9S in answer flop)
        - 2C: green (exact match in answer flop)
        - AD: grey (no match)
        - 3D: grey (no match)
        """
        guess = [Card.from_string(c) for c in ["4C", "9H", "2C", "AD", "3D"]]
        answer = [Card.from_string(c) for c in ["2C", "9S", "2S", "4S", "5S"]]
        guess_index = np.array([[card.card_index for card in guess]], dtype=np.int8)
        answer_index = np.array([[card.card_index for card in answer]], dtype=np.int8)

        result = np.zeros(1, dtype=np.int16)
        Solver._Solver__compare_tables(guess_index, answer_index, result)  # type: ignore[attr-defined]

        # Expected: grey=0, yellow=1, green=2, grey=0, grey=0 -> 01200
        assert result[0] == 1200, (
            f"Expected 01200 (grey, yellow, green, grey, grey) but got {result[0]:05d}. "
            "Green matches should be found before yellow matches consume the answer card."
        )


class TestRankHandBestHandTuple:
    """Test that rank_hand returns correct best_hand tuples.

    These tests ensure that the best_hand tuple contains the correct number
    of cards for each hand type. This is critical because the solver uses
    best_hand to track which cards are used in card_used_accumulated,
    which affects the validation logic and final table count.
    """

    def test_high_card_best_hand_has_5_cards(self):
        """Test that high card returns exactly 1 card in best_hand (the high card itself)."""
        table = [Card(2, "H"), Card(5, "D"), Card(9, "S")]
        hole = [Card(10, "C"), Card(13, "H")]

        ranking = Solver._Solver__rank_hand(table, hole)

        assert ranking.rank == 1  # High card
        assert len(ranking.best_hand) == 1  # Only stores the high card
        assert ranking.best_hand[0].rank == 13  # King is the high card
        assert ranking.tie_breakers == (13, 10, 9, 5, 2)

    def test_one_pair_best_hand_has_2_cards(self):
        """Test that one pair returns exactly 2 cards in best_hand."""
        table = [Card(10, "H"), Card(10, "D"), Card(5, "S")]
        hole = [Card(7, "C"), Card(13, "H")]

        ranking = Solver._Solver__rank_hand(table, hole)

        assert ranking.rank == 2  # One pair
        assert len(ranking.best_hand) == 2
        assert all(c.rank == 10 for c in ranking.best_hand)

    def test_two_pair_best_hand_has_4_cards(self):
        """Test that two pair returns exactly 4 cards in best_hand."""
        table = [Card(10, "H"), Card(10, "D"), Card(5, "S")]
        hole = [Card(5, "C"), Card(13, "H")]

        ranking = Solver._Solver__rank_hand(table, hole)

        assert ranking.rank == 3  # Two pair
        assert len(ranking.best_hand) == 4
        # Should have two 10s and two 5s
        ranks = sorted([c.rank for c in ranking.best_hand], reverse=True)
        assert ranks == [10, 10, 5, 5]

    def test_three_of_a_kind_best_hand_has_3_cards(self):
        """Test that three of a kind returns exactly 3 cards in best_hand."""
        table = [Card(10, "H"), Card(10, "D"), Card(10, "S")]
        hole = [Card(7, "C"), Card(13, "H")]

        ranking = Solver._Solver__rank_hand(table, hole)

        assert ranking.rank == 4  # Three of a kind
        assert len(ranking.best_hand) == 3
        assert all(c.rank == 10 for c in ranking.best_hand)

    def test_straight_best_hand_has_5_cards(self):
        """Test that straight returns exactly 5 cards in best_hand."""
        table = [Card(10, "H"), Card(11, "D"), Card(12, "S")]
        hole = [Card(13, "C"), Card(14, "H")]

        ranking = Solver._Solver__rank_hand(table, hole)

        assert ranking.rank == 5  # Straight
        assert len(ranking.best_hand) == 5
        assert ranking.tie_breakers == (14,)  # Ace-high straight

    def test_straight_with_duplicate_ranks_includes_all_needed_cards(self):
        """Test that straight includes cards even with duplicate ranks on board.

        This test is critical because when there are duplicate ranks in the
        straight range, the cards_used_accumulated set must include the right
        cards to pass validation. Previously, an optimization incorrectly
        selected only one card per rank, which caused the solver to report
        incorrect table counts.
        """
        # Board has two 10s, both in the straight range
        table = [
            Card(10, "H"),
            Card(10, "C"),
            Card(11, "D"),
            Card(12, "S"),
            Card(13, "H"),
        ]
        hole = [Card(14, "H"), Card(2, "D")]

        ranking = Solver._Solver__rank_hand(table, hole)

        assert ranking.rank == 5  # Straight
        assert len(ranking.best_hand) == 5
        # Best hand should contain 5 cards from the straight (10-14)
        straight_ranks = sorted([c.rank for c in ranking.best_hand], reverse=True)
        assert straight_ranks == [14, 13, 12, 11, 10]

    def test_ace_low_straight_best_hand_has_5_cards(self):
        """Test that ace-low straight (wheel) returns exactly 5 cards."""
        table = [Card(2, "H"), Card(3, "D"), Card(4, "S")]
        hole = [Card(5, "C"), Card(14, "H")]

        ranking = Solver._Solver__rank_hand(table, hole)

        assert ranking.rank == 5  # Straight
        assert len(ranking.best_hand) == 5
        assert ranking.tie_breakers == (5,)  # 5-high (wheel)

    def test_flush_best_hand_has_5_cards(self):
        """Test that flush returns exactly 5 cards in best_hand."""
        table = [Card(2, "H"), Card(5, "H"), Card(9, "H")]
        hole = [Card(11, "H"), Card(13, "H")]

        ranking = Solver._Solver__rank_hand(table, hole)

        assert ranking.rank == 6  # Flush
        assert len(ranking.best_hand) == 5
        assert all(c.suit == "H" for c in ranking.best_hand)

    def test_full_house_best_hand_has_5_cards(self):
        """Test that full house returns exactly 5 cards in best_hand."""
        table = [Card(10, "H"), Card(10, "D"), Card(10, "S")]
        hole = [Card(5, "C"), Card(5, "H")]

        ranking = Solver._Solver__rank_hand(table, hole)

        assert ranking.rank == 7  # Full house
        assert len(ranking.best_hand) == 5
        # Should have three 10s and two 5s
        ranks = sorted([c.rank for c in ranking.best_hand], reverse=True)
        assert ranks == [10, 10, 10, 5, 5]

    def test_four_of_a_kind_best_hand_has_4_cards(self):
        """Test that four of a kind returns exactly 4 cards in best_hand."""
        table = [
            Card(10, "H"),
            Card(10, "D"),
            Card(10, "S"),
            Card(10, "C"),
            Card(5, "C"),
        ]
        hole = [Card(7, "H"), Card(2, "D")]

        ranking = Solver._Solver__rank_hand(table, hole)

        assert ranking.rank == 8  # Four of a kind
        assert len(ranking.best_hand) == 4
        assert all(c.rank == 10 for c in ranking.best_hand)

    def test_straight_flush_best_hand_has_5_cards(self):
        """Test that straight flush returns exactly 5 cards in best_hand."""
        table = [Card(10, "H"), Card(11, "H"), Card(12, "H")]
        hole = [Card(13, "H"), Card(14, "H")]

        ranking = Solver._Solver__rank_hand(table, hole)

        assert ranking.rank == 9  # Straight flush
        assert len(ranking.best_hand) == 5
        assert all(c.suit == "H" for c in ranking.best_hand)
        assert ranking.tie_breakers == (14,)


class TestSolverTableCountRegression:
    """Regression tests to ensure solver returns correct number of possible tables.

    These tests verify that optimizations to rank_hand don't inadvertently change
    the solver's output by affecting the cards_used_accumulated validation logic.
    """

    def test_specific_scenario_returns_1474_tables(self):
        """Test the specific scenario that previously returned 1468 instead of 1474.

        This regression test ensures that when rank_hand was optimized, it still
        produces the exact same solver results. The bug was that best_hand for
        high card only returned 1 card instead of 5, which affected cards_used_accumulated.
        """
        p1_hole = [Card.from_string("7C"), Card.from_string("9D")]
        p2_hole = [Card.from_string("KH"), Card.from_string("KS")]
        p3_hole = [Card.from_string("8D"), Card.from_string("4S")]

        flop = [1, 2, 3]
        turn = [3, 1, 2]
        river = [2, 3, 1]

        solver = Solver(p1_hole, p2_hole, p3_hole, flop, turn, river)
        possible_tables = solver.solve()

        # The critical assertion: must find exactly 1474 possible tables
        assert len(possible_tables) == 1474

    def test_solver_produces_consistent_results_across_runs(self):
        """Test that solver produces identical results across multiple runs.

        This ensures that any card selection in rank_hand is deterministic.
        """
        p1_hole = [Card.from_string("7C"), Card.from_string("9D")]
        p2_hole = [Card.from_string("KH"), Card.from_string("KS")]
        p3_hole = [Card.from_string("8D"), Card.from_string("4S")]

        flop = [1, 2, 3]
        turn = [3, 1, 2]
        river = [2, 3, 1]

        # Run solver multiple times
        results = []
        for _ in range(3):
            solver = Solver(p1_hole, p2_hole, p3_hole, flop, turn, river)
            possible_tables = solver.solve()
            results.append(len(possible_tables))

        # All runs should produce identical counts
        assert all(count == results[0] for count in results)
        assert results[0] == 1474


class TestSolverTableCountRegressionKickerBug:
    """Regression tests for the kicker card bug found on Jan 13, 2026.

    This bug was introduced in commit 1901440 on Dec 28, 2025 when the
    rank_hand method was 'optimized'. The buggy version produced incorrect
    kicker selection for pairs, two pairs, and three of a kind, causing
    the solver to accept invalid tables where not all table cards were used.

    These tests validate the exact table counts for scenarios that caught
    the bug: slow_output and very_slow.
    """

    def test_slow_output_scenario_exact_count(self):
        """Test that slow_output scenario produces exactly 1,323 tables.

        This was the primary test case that caught the bug:
        - Buggy version: 20,873 tables (15.8x too many)
        - Correct version: 1,323 tables
        """
        p1 = [Card.from_string("KH"), Card.from_string("6S")]
        p2 = [Card.from_string("8C"), Card.from_string("8H")]
        p3 = [Card.from_string("4H"), Card.from_string("9S")]

        solver = Solver(p1, p2, p3, [2, 3, 1], [3, 2, 1], [3, 1, 2])
        tables = solver.solve()

        assert len(tables) == 1323, (
            f"slow_output scenario should produce exactly 1,323 tables, "
            f"but got {len(tables)}. This may indicate a regression in "
            f"kicker card selection logic."
        )

    def test_very_slow_scenario_exact_count(self):
        """Test that very_slow scenario produces exactly 7,606 tables.

        This was the secondary test case that confirmed the bug:
        - Buggy version: 14,528 tables (1.9x too many)
        - Correct version: 7,606 tables
        """
        p1 = [Card.from_string("JH"), Card.from_string("6H")]
        p2 = [Card.from_string("4H"), Card.from_string("7S")]
        p3 = [Card.from_string("5D"), Card.from_string("8D")]

        solver = Solver(p1, p2, p3, [3, 2, 1], [2, 3, 1], [2, 1, 3])
        tables = solver.solve()

        assert len(tables) == 7606, (
            f"very_slow scenario should produce exactly 7,606 tables, "
            f"but got {len(tables)}. This may indicate a regression in "
            f"kicker card selection logic."
        )

    def test_kicker_sorting_with_multiple_same_rank_cards(self):
        """Test that kicker selection works correctly when multiple cards share ranks.

        The bug was caused by sorting ranks directly instead of sorting cards
        and then extracting ranks. This test verifies correct behavior when
        there are multiple cards of the same rank among potential kickers.
        """
        # Setup: Three of a kind (10s) with distinct kickers (7, 5, 4, 3)
        table = [
            Card(10, "H"),
            Card(10, "D"),
            Card(10, "S"),
            Card(7, "H"),
            Card(5, "C"),
        ]
        hole = [Card(4, "D"), Card(3, "S")]

        ranking = Solver._Solver__rank_hand(table, hole)

        # Should be three of a kind (rank 4)
        assert ranking.rank == 4
        # Kickers should be the two highest ranks from non-trips: 7 and 5
        assert ranking.tie_breakers == (10, 7, 5)
        # best_hand should only contain the three 10s
        assert len(ranking.best_hand) == 3
        assert all(c.rank == 10 for c in ranking.best_hand)

    def test_two_pair_kicker_selection_deterministic(self):
        """Test that two pair kicker is selected deterministically.

        The bug affected how the kicker was selected from remaining cards.
        This ensures the highest kicker is always chosen correctly.
        """
        # Two pair: 10s and 5s, with kicker options 8, 3, 2
        table = [Card(10, "H"), Card(10, "D"), Card(5, "S")]
        hole = [Card(5, "H"), Card(8, "C")]
        extra_cards = [Card(3, "C"), Card(2, "D")]

        ranking = Solver._Solver__rank_hand(table + extra_cards, hole)

        assert ranking.rank == 3  # Two pair
        assert ranking.tie_breakers == (10, 5, 8)  # Should pick 8 as kicker, not 3 or 2
        assert len(ranking.best_hand) == 4  # Only the two pairs

    def test_one_pair_multiple_kickers_correct_order(self):
        """Test that one pair selects kickers in correct descending order.

        The buggy version could select kickers in wrong order when using
        rank_groups.keys() directly instead of sorting actual cards.
        """
        # One pair of 10s with kickers 14, 9, 5, 3, 2
        table = [Card(10, "H"), Card(10, "D"), Card(9, "S")]
        hole = [Card(14, "H"), Card(5, "C")]
        extra_cards = [Card(3, "D"), Card(2, "S")]

        ranking = Solver._Solver__rank_hand(table + extra_cards, hole)

        assert ranking.rank == 2  # One pair
        # Kickers should be top 3: Ace (14), 9, 5
        assert ranking.tie_breakers == (10, 14, 9, 5)
        assert len(ranking.best_hand) == 2  # Only the pair
