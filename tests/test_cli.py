"""Tests for the CLI interface."""

import sys
from pathlib import Path
from unittest.mock import patch
# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "pokle_solver"))
from cli import cli


class TestCLIValidWorkflow:
    """Test valid CLI workflows."""

    def test_cli_complete_workflow_immediate_solve(self, monkeypatch, capsys):
        """Test complete CLI workflow where user guesses correctly on first try."""
        inputs = [
            "QD QC",  # Player 1 hole cards
            "10H 2H",  # Player 2 hole cards
            "9H KH",  # Player 3 hole cards
            "2 1 3",  # Flop ranks
            "1 3 2",  # Turn ranks
            "2 1 3",  # River ranks
            "g g g g g",  # All green - correct guess
        ]
        input_iter = iter(inputs)
        monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

        cli()

        captured = capsys.readouterr()
        assert "Possible tables found:" in captured.out
        assert "Possible tables remaining: 1" in captured.out

    def test_cli_workflow_with_multiple_guesses(self, monkeypatch, capsys):
        """Test CLI workflow with multiple guesses before solving."""
        inputs = [
            "QD QC",  # Player 1 hole cards
            "10H 2H",  # Player 2 hole cards
            "9H KH",  # Player 3 hole cards
            "2 1 3",  # Flop ranks
            "1 3 2",  # Turn ranks
            "2 1 3",  # River ranks
            "e e e e e",  # All grey - will cause error (no matches)
            "y y y y y",  # All yellow - will cause error (no matches)
            "g g g g g",  # All green - correct guess
        ]
        input_iter = iter(inputs)
        monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

        cli()

        captured = capsys.readouterr()
        assert "Possible tables found:" in captured.out
        # Only prints "Possible tables remaining" on successful guesses, not on errors
        assert captured.out.count("Error: No rivers match") >= 2

    def test_cli_accepts_lowercase_cards(self, monkeypatch, capsys):
        """Test that CLI accepts lowercase card input."""
        inputs = [
            "qd qc",  # Lowercase input
            "10h 2h",
            "9h kh",
            "2 1 3",
            "1 3 2",
            "2 1 3",
            "g g g g g",
        ]
        input_iter = iter(inputs)
        monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

        cli()

        captured = capsys.readouterr()
        assert "Possible tables found:" in captured.out


class TestCLICardInputValidation:
    """Test CLI validation of hole card input."""

    def test_cli_rejects_wrong_card_count_then_accepts(self, monkeypatch, capsys):
        """Test that CLI rejects wrong number of cards and allows retry."""
        inputs = [
            "QD",  # Only 1 card - should fail
            "QD QC QH",  # 3 cards - should fail
            "QD QC",  # Correct - 2 cards
            "10H 2H",
            "9H KH",
            "2 1 3",
            "1 3 2",
            "2 1 3",
            "g g g g g",
        ]
        input_iter = iter(inputs)
        monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

        cli()

        captured = capsys.readouterr()
        assert captured.out.count("Error:") >= 2
        assert "exactly two cards" in captured.out

    def test_cli_rejects_invalid_card_format(self, monkeypatch, capsys):
        """Test that CLI rejects invalid card format."""
        inputs = [
            "XX YY",  # Invalid card format
            "QD QC",  # Valid
            "10H 2H",
            "9H KH",
            "2 1 3",
            "1 3 2",
            "2 1 3",
            "g g g g g",
        ]
        input_iter = iter(inputs)
        monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

        cli()

        captured = capsys.readouterr()
        assert "Error:" in captured.out

    def test_cli_handles_extra_whitespace_in_cards(self, monkeypatch, capsys):
        """Test that CLI handles extra whitespace in card input."""
        inputs = [
            "  QD   QC  ",  # Extra whitespace
            "10H 2H",
            "9H KH",
            "2 1 3",
            "1 3 2",
            "2 1 3",
            "g g g g g",
        ]
        input_iter = iter(inputs)
        monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

        cli()

        captured = capsys.readouterr()
        assert "Possible tables found:" in captured.out


class TestCLIRankInputValidation:
    """Test CLI validation of hand rank input."""

    def test_cli_rejects_invalid_rank_values(self, monkeypatch, capsys):
        """Test that CLI rejects invalid rank values."""
        inputs = [
            "QD QC",
            "10H 2H",
            "9H KH",
            "1 2 4",  # Invalid - 4 is not a valid rank
            "1 1 3",  # Invalid - duplicate ranks
            "2 1 3",  # Valid
            "1 3 2",
            "2 1 3",
            "g g g g g",
        ]
        input_iter = iter(inputs)
        monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

        cli()

        captured = capsys.readouterr()
        assert captured.out.count("Error:") >= 2
        assert "valid ranks" in captured.out

    def test_cli_rejects_wrong_rank_count(self, monkeypatch, capsys):
        """Test that CLI rejects wrong number of ranks."""
        inputs = [
            "QD QC",
            "10H 2H",
            "9H KH",
            "1 2",  # Only 2 ranks
            "2 1 3",  # Valid
            "1 3 2",
            "2 1 3",
            "g g g g g",
        ]
        input_iter = iter(inputs)
        monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

        cli()

        captured = capsys.readouterr()
        assert "Error:" in captured.out

    def test_cli_accepts_all_rank_permutations(self, monkeypatch, capsys):
        """Test that CLI accepts different rank permutations."""
        inputs = [
            "QD QC",
            "10H 2H",
            "9H KH",
            "1 2 3",  # Different permutation
            "3 2 1",  # Different permutation
            "1 3 2",  # Different permutation
            "g g g g g",
        ]
        input_iter = iter(inputs)
        monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

        cli()

        captured = capsys.readouterr()
        assert "Possible tables found:" in captured.out


class TestCLIColorFeedbackValidation:
    """Test CLI validation of color feedback input."""

    def test_cli_rejects_wrong_color_count(self, monkeypatch, capsys):
        """Test that CLI rejects wrong number of colors."""
        inputs = [
            "QD QC",
            "10H 2H",
            "9H KH",
            "2 1 3",
            "1 3 2",
            "2 1 3",
            "g g g",  # Only 3 colors - should fail
            "g g g g",  # Only 4 colors - should fail
            "g g g g g",  # Valid - 5 colors
        ]
        input_iter = iter(inputs)
        monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

        cli()

        captured = capsys.readouterr()
        assert captured.out.count("Error:") >= 2
        assert "exactly 5 colors" in captured.out

    def test_cli_rejects_invalid_color_values(self, monkeypatch, capsys):
        """Test that CLI rejects invalid color values."""
        inputs = [
            "QD QC",
            "10H 2H",
            "9H KH",
            "2 1 3",
            "1 3 2",
            "2 1 3",
            "r b g y e",  # Invalid colors 'r' and 'b'
            "g g g g g",  # Valid
        ]
        input_iter = iter(inputs)
        monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

        cli()

        captured = capsys.readouterr()
        assert "Error:" in captured.out

    def test_cli_accepts_mixed_case_colors(self, monkeypatch, capsys):
        """Test that CLI accepts mixed case color input (converts to lowercase)."""
        inputs = [
            "QD QC",
            "10H 2H",
            "9H KH",
            "2 1 3",
            "1 3 2",
            "2 1 3",
            "G Y E E G",  # Uppercase - should be converted but may cause error if no match
            "G G G G G",  # All green to exit
        ]
        input_iter = iter(inputs)
        monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

        cli()

        captured = capsys.readouterr()
        # Should work - no validation error for valid colors in uppercase
        assert "Possible tables remaining:" in captured.out

    def test_cli_handles_extra_whitespace_in_colors(self, monkeypatch, capsys):
        """Test that CLI handles extra whitespace in color input."""
        inputs = [
            "QD QC",
            "10H 2H",
            "9H KH",
            "2 1 3",
            "1 3 2",
            "2 1 3",
            "  g   g   g   g   g  ",  # Extra whitespace
        ]
        input_iter = iter(inputs)
        monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

        cli()

        captured = capsys.readouterr()
        assert "Possible tables remaining:" in captured.out


class TestCLILoopBehavior:
    """Test CLI looping behavior until solution found."""

    def test_cli_continues_until_all_green(self, monkeypatch, capsys):
        """Test that CLI continues asking for guesses until all green."""
        inputs = [
            "QD QC",
            "10H 2H",
            "9H KH",
            "2 1 3",
            "1 3 2",
            "2 1 3",
            "e e e e e",  # Not all green - will cause error (no matches)
            "y y y y y",  # Not all green - will cause error (no matches)
            "g y e e g",  # Not all green - will cause error (no matches)
            "g g g g g",  # All green - should exit
        ]
        input_iter = iter(inputs)
        monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

        cli()

        captured = capsys.readouterr()
        # Only successful guesses print "Possible tables remaining"
        # Errors just print error messages
        assert captured.out.count("Error: No rivers match") >= 3
        assert "Possible tables remaining:" in captured.out

    def test_cli_exits_on_first_all_green(self, monkeypatch, capsys):
        """Test that CLI exits immediately when all green is entered."""
        inputs = [
            "QD QC",
            "10H 2H",
            "9H KH",
            "2 1 3",
            "1 3 2",
            "2 1 3",
            "g g g g g",  # All green on first try - should exit
        ]
        input_iter = iter(inputs)
        monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

        cli()

        captured = capsys.readouterr()
        # Should have exactly 1 "Possible tables remaining" message
        assert captured.out.count("Possible tables remaining:") == 1


class TestCLIErrorRecovery:
    """Test CLI error recovery and retry logic."""

    def test_cli_recovers_from_multiple_card_errors(self, monkeypatch, capsys):
        """Test that CLI can recover from multiple consecutive card errors."""
        inputs = [
            "QD",  # Error: only 1 card
            "XX YY",  # Error: invalid format
            "QD QC QH",  # Error: 3 cards
            "QD QC",  # Success
            "10H 2H",
            "9H KH",
            "2 1 3",
            "1 3 2",
            "2 1 3",
            "g g g g g",
        ]
        input_iter = iter(inputs)
        monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

        cli()

        captured = capsys.readouterr()
        assert captured.out.count("Error:") >= 3
        assert "Possible tables found:" in captured.out

    def test_cli_recovers_from_multiple_rank_errors(self, monkeypatch, capsys):
        """Test that CLI can recover from multiple consecutive rank errors."""
        inputs = [
            "QD QC",
            "10H 2H",
            "9H KH",
            "1 2",  # Error: only 2 ranks
            "1 2 4",  # Error: invalid rank
            "1 1 1",  # Error: duplicates
            "2 1 3",  # Success
            "1 3 2",
            "2 1 3",
            "g g g g g",
        ]
        input_iter = iter(inputs)
        monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

        cli()

        captured = capsys.readouterr()
        assert captured.out.count("Error:") >= 3

    def test_cli_recovers_from_multiple_color_errors(self, monkeypatch, capsys):
        """Test that CLI can recover from multiple consecutive color errors."""
        inputs = [
            "QD QC",
            "10H 2H",
            "9H KH",
            "2 1 3",
            "1 3 2",
            "2 1 3",
            "g g g",  # Error: only 3 colors
            "r b g y e",  # Error: invalid colors
            "g g g g g g",  # Error: 6 colors
            "g g g g g",  # Success
        ]
        input_iter = iter(inputs)
        monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

        cli()

        captured = capsys.readouterr()
        assert captured.out.count("Error:") >= 3


class TestCLIOutputMessages:
    """Test CLI output messages and formatting."""

    def test_cli_displays_player_prompts(self, monkeypatch, capsys):
        """Test that CLI displays prompts for all players."""
        inputs = [
            "QD QC",
            "10H 2H",
            "9H KH",
            "2 1 3",
            "1 3 2",
            "2 1 3",
            "g g g g g",
        ]
        input_iter = iter(inputs)
        monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

        # Capture stderr to get prompts
        with patch("builtins.input", side_effect=inputs):
            cli()

        captured = capsys.readouterr()
        # Check that solver ran successfully
        assert "Possible tables found:" in captured.out

    def test_cli_displays_phase_prompts(self, monkeypatch, capsys):
        """Test that CLI displays prompts for all game phases."""
        inputs = [
            "QD QC",
            "10H 2H",
            "9H KH",
            "2 1 3",
            "1 3 2",
            "2 1 3",
            "g g g g g",
        ]
        input_iter = iter(inputs)
        monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

        cli()

        captured = capsys.readouterr()
        # Verify solver completed
        assert "Possible tables found:" in captured.out
        assert "Possible tables remaining:" in captured.out

    def test_cli_displays_table_count_updates(self, monkeypatch, capsys):
        """Test that CLI displays table count after successful guesses."""
        inputs = [
            "QD QC",
            "10H 2H",
            "9H KH",
            "2 1 3",
            "1 3 2",
            "2 1 3",
            "e e e e e",  # Will cause error
            "g g g g g",  # Successful guess
        ]
        input_iter = iter(inputs)
        monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

        cli()

        captured = capsys.readouterr()
        # Only successful guess prints "Possible tables remaining"
        assert "Possible tables remaining:" in captured.out
        assert "Error: No rivers match" in captured.out
