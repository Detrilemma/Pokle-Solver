# Pokle Solver

An automated solver for [Pokle](https://pokle.app/), a daily poker hand ranking puzzle game inspired by Wordle.

## Overview

Pokle challenges players to identify the winning poker hand across three rounds (flop, turn, and river) using color-coded feedback. This solver uses advanced algorithmic techniques to efficiently narrow down valid poker hands and provide optimal guesses.

## Features

- **Intelligent Solving Algorithm**: Uses Numba-optimized comparison logic with two-pass matching for position-agnostic flop cards
- **Browser Automation**: Playwright integration for automatic game playing via `auto_solve.py`
- **Color Feedback System**: 
  - 🟢 Green: Exact match (correct card in correct position)
  - 🟡 Yellow: Card rank or suit appears elsewhere in the hand
  - ⚫ Grey: Card rank and suit not in the answer
- **Sampling Optimization**: Efficient sampling strategies to reduce computational overhead
- **Comprehensive Test Suite**: Unit and integration tests ensuring solver accuracy

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd pokle_solver

# Install dependencies using Poetry
poetry install

# Install Playwright browsers (for auto-solve functionality)
poetry run playwright install
```

## Usage

### Manual Solving

```python
from pokle_solver import Solver
from pokle_solver.card import Card

# Define hole cards for three players
p1_cards = [Card.from_string("AH"), Card.from_string("KD")]
p2_cards = [Card.from_string("QC"), Card.from_string("JS")]
p3_cards = [Card.from_string("10H"), Card.from_string("9D")]

# Define placements for each round (flop, turn, river)
flop_places = [1, 2, 3]  # Player 1 wins, Player 2 second, Player 3 third
turn_places = [2, 1, 3]
river_places = [1, 3, 2]

# Initialize solver
solver = Solver(
    p1_cards, p2_cards, p3_cards,
    flop_places, turn_places, river_places
)

# Get initial guess
guess = solver.get_maxh_table(use_sampling=True)
print(f"First guess: {guess}")

# Submit guess and get color feedback
card_colors = ["g", "y", "e", "g", "y"]  # Example feedback

# Update solver with feedback
solver.next_table_guess(card_colors)

# Continue until all green
```

### Automated Browser Solving

```bash
# Run the auto-solver (opens browser and plays automatically)
poetry run python src/pokle_solver/auto_solve.py
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run specific test suite
poetry run pytest tests/test_solver_unit.py -v

# Run auto-solve tests
poetry run pytest tests/test_auto_solve.py -v

# Check code coverage
poetry run pytest --cov=pokle_solver
```

## Project Structure

```
pokle_solver/
├── src/pokle_solver/
│   ├── __init__.py
│   ├── card.py          # Card representation and utilities
│   ├── solver.py        # Core solving algorithm
│   ├── auto_solve.py    # Browser automation with Playwright
│   ├── cli.py           # Command-line interface
│   └── example.py       # Testing utilities and examples
├── tests/
│   ├── test_card.py
│   ├── test_solver_unit.py
│   ├── test_solver_integration.py
│   ├── test_auto_solve.py
│   └── test_cli.py
├── pyproject.toml       # Project dependencies and configuration
└── README.md
```

## How It Works

The solver employs a constraint satisfaction approach:

1. **Initial State**: Generates all possible 5-card combinations from the remaining deck (excluding known hole cards)
2. **Ranking**: Evaluates poker hand strength for each player with each possible table
3. **Filtering**: Eliminates tables inconsistent with observed round placements
4. **Guessing Strategy**: Selects the table that maximizes information gain (highest entropy)
5. **Feedback Processing**: 
   - Green matches are locked in position
   - Yellow matches indicate rank/suit exists elsewhere
   - Grey matches eliminate cards from consideration
6. **Iteration**: Repeats until solution converges (all green feedback)

### Key Optimizations

- **Numba JIT Compilation**: `__compare_tables` uses `@guvectorize` for efficient parallel processing
- **Two-Pass Matching**: Flop cards match green positions first, then yellow (position-agnostic)
- **Sampling**: Reduces search space for large valid table sets
- **DOM Reliability**: Index-based selectors with `.last` ensure accurate color feedback extraction

## Development

### Code Quality

```bash
# Format code
poetry run ruff format

# Lint code
poetry run ruff check --fix

# Type checking (if configured)
poetry run mypy src/
```

### Contributing

1. Create a feature branch: `git switch -c feature-name`
2. Make changes and add tests
3. Ensure all tests pass: `poetry run pytest`
4. Format and lint: `poetry run ruff format && ruff check --fix`
5. Commit changes: `git commit -m "Description"`
6. Push and open a pull request

## License

[Add license information]

## Acknowledgments

- Inspired by the daily [Pokle](https://pokle.app/) puzzle game
- Built with Python, Numba, and Playwright