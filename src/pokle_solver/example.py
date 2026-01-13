"""Example script demonstrating Pokle solver usage.

Provides a sandbox environment for testing the solver with pre-configured
scenarios. Useful for development and testing.

This script can be run either as a module (python -m pokle_solver.example)
or directly as a script (python example.py).

Classes:
    PokleTestCase: Configuration for a Pokle game scenario

Functions:
    sandbox: Run solver with example configuration
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

from dataclasses import dataclass
from typing import List, Optional
import polars as pl


@dataclass
class PokleTestCase:
    """Configuration for a Pokle game scenario.
    
    Attributes:
        name: Descriptive name for this test case
        p1_hole: Player 1's hole cards (list of Card objects)
        p2_hole: Player 2's hole cards (list of Card objects)
        p3_hole: Player 3's hole cards (list of Card objects)
        flop_rankings: Hand rankings at flop [1=best, 2=second, 3=third]
        turn_rankings: Hand rankings at turn [1=best, 2=second, 3=third]
        river_rankings: Hand rankings at river [1=best, 2=second, 3=third]
        expected_rivers: Expected number of valid rivers (for validation)
    """
    name: str
    p1_hole: List[Card]
    p2_hole: List[Card]
    p3_hole: List[Card]
    flop_rankings: List[int]
    turn_rankings: List[int]
    river_rankings: List[int]
    expected_rivers: Optional[int] = None  # Optional: for validation
    
    def __post_init__(self):
        """Validate that all hole cards are Card objects and rankings are valid."""
        # Validate hole cards are Card objects
        for player, holes in [("P1", self.p1_hole), ("P2", self.p2_hole), ("P3", self.p3_hole)]:
            if not isinstance(holes, list) or len(holes) != 2:
                raise ValueError(f"{player} hole cards must be a list of 2 cards")
            if not all(isinstance(card, Card) for card in holes):
                raise ValueError(f"All {player} hole cards must be Card objects")
        
        # Validate rankings
        for phase, rankings in [
            ("flop", self.flop_rankings),
            ("turn", self.turn_rankings),
            ("river", self.river_rankings),
        ]:
            if sorted(rankings) != [1, 2, 3]:
                raise ValueError(
                    f"{phase} rankings must be a permutation of [1, 2, 3], got {rankings}"
                )
    
    @classmethod
    def from_strings(
        cls,
        name: str,
        p1_hole_strs: List[str],
        p2_hole_strs: List[str],
        p3_hole_strs: List[str],
        flop_rankings: List[int],
        turn_rankings: List[int],
        river_rankings: List[int],
        expected_rivers: Optional[int] = None,
    ):
        """Create test case from string card representations.
        
        Args:
            name: Test case name
            p1_hole_strs: Player 1 hole cards as strings (e.g., ["KH", "6S"])
            p2_hole_strs: Player 2 hole cards as strings
            p3_hole_strs: Player 3 hole cards as strings
            flop_rankings: Rankings at flop
            turn_rankings: Rankings at turn
            river_rankings: Rankings at river
            expected_rivers: Expected number of valid rivers
            
        Returns:
            PokleTestCase instance with Card objects
        """
        return cls(
            name=name,
            p1_hole=[Card.from_string(s) for s in p1_hole_strs],
            p2_hole=[Card.from_string(s) for s in p2_hole_strs],
            p3_hole=[Card.from_string(s) for s in p3_hole_strs],
            flop_rankings=flop_rankings,
            turn_rankings=turn_rankings,
            river_rankings=river_rankings,
            expected_rivers=expected_rivers,
        )
    
    def create_solver(self) -> Solver:
        """Create a Solver instance from this test case."""
        return Solver(
            self.p1_hole,
            self.p2_hole,
            self.p3_hole,
            self.flop_rankings,
            self.turn_rankings,
            self.river_rankings,
        )


# Pre-configured test cases for calibration study
TEST_CASES = {
    "first_example": PokleTestCase.from_strings(
        name="First Example",
        p1_hole_strs=["6H", "8H"],
        p2_hole_strs=["QS", "JC"],
        p3_hole_strs=["4H", "JD"],
        flop_rankings=[2, 1, 3],
        turn_rankings=[2, 3, 1],
        river_rankings=[3, 2, 1],
    ),
    "fast_example": PokleTestCase.from_strings(
        name="Fast Example",
        p1_hole_strs=["QD", "QC"],
        p2_hole_strs=["10H", "2H"],
        p3_hole_strs=["9H", "KH"],
        flop_rankings=[2, 1, 3],
        turn_rankings=[1, 3, 2],
        river_rankings=[2, 1, 3],
    ),
    "example_12_14": PokleTestCase.from_strings(
        name="Example 12/14",
        p1_hole_strs=["4D", "AH"],
        p2_hole_strs=["8C", "QS"],
        p3_hole_strs=["9D", "JS"],
        flop_rankings=[3, 2, 1],
        turn_rankings=[2, 3, 1],
        river_rankings=[3, 2, 1],
    ),
    "example_12_25": PokleTestCase.from_strings(
        name="Example 12/25",
        p1_hole_strs=["7C", "9D"],
        p2_hole_strs=["KH", "KS"],
        p3_hole_strs=["8D", "4S"],
        flop_rankings=[1, 2, 3],
        turn_rankings=[3, 1, 2],
        river_rankings=[2, 3, 1],
    ),
    "example_1_12": PokleTestCase.from_strings(
        name="Example 1/12",
        p1_hole_strs=["6D", "JC"],
        p2_hole_strs=["10S", "QS"],
        p3_hole_strs=["4C", "4D"],
        flop_rankings=[1, 3, 2],
        turn_rankings=[1, 2, 3],
        river_rankings=[2, 1, 3],
    ),
    "slow_output": PokleTestCase.from_strings(
        name="Slow Output Test",
        p1_hole_strs=["KH", "6S"],
        p2_hole_strs=["8C", "8H"],
        p3_hole_strs=["4H", "9S"],
        flop_rankings=[2, 3, 1],
        turn_rankings=[3, 2, 1],
        river_rankings=[3, 1, 2],
    ),
    "very_slow": PokleTestCase.from_strings(
        name="Very Slow Output Test",
        p1_hole_strs=["JH", "6H"],
        p2_hole_strs=["4H", "7S"],
        p3_hole_strs=["5D", "8D"],
        flop_rankings=[3, 2, 1],
        turn_rankings=[2, 3, 1],
        river_rankings=[2, 1, 3],
    ),
    "example_1_13": PokleTestCase.from_strings(
        name="Example 1/13",
        p1_hole_strs=["AD", "QH"],
        p2_hole_strs=["8C", "4C"],
        p3_hole_strs=["9C", "7D"],
        flop_rankings=[1, 2, 3],
        turn_rankings=[2, 1, 3],
        river_rankings=[2, 1, 3],
    )
}
def sample_sandbox():
    for test_name, test_case in TEST_CASES.items():
        print(f"Running test case: {test_name} - {test_case.name}")
        solver = test_case.create_solver()
        possible_tables = solver.solve()
        print(f"Possible tables found: {len(possible_tables)}")

def sandbox():
    """Interactive game loop using pre-configured test case."""
    # Use current example (1/12)
    test_case = TEST_CASES["example_1_12"]
    
    solver = test_case.create_solver()
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
    sample_sandbox()