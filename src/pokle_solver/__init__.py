"""Pokle Solver - Find valid poker table runouts given hand ranking constraints.

This package provides tools for solving Pokle games by finding all possible
table configurations that match specified hand rankings across game phases.

Main classes:
    - Solver: Core solver for finding valid tables
    - Card: Immutable playing card representation
    - ColorCard: Card with color feedback for guessing

Example:
    >>> from pokle_solver import Solver, Card
    >>> solver = Solver(
    ...     p1hole=[Card(14, 'H'), Card(13, 'H')],
    ...     p2hole=[Card(10, 'D'), Card(10, 'C')],
    ...     p3hole=[Card(7, 'S'), Card(2, 'S')],
    ...     flop_hand_ranks=[2, 1, 3],
    ...     turn_hand_ranks=[1, 2, 3],
    ...     river_hand_ranks=[1, 2, 3]
    ... )
    >>> tables = solver.solve()
    >>> print(f"Found {len(tables)} possible tables")
"""

from pokle_solver.card import Card, ColorCard
from pokle_solver.solver import Solver, HandRanking, PhaseEvaluation

__version__ = "0.1.0"
__all__ = ["Card", "ColorCard", "Solver", "HandRanking", "PhaseEvaluation"]
