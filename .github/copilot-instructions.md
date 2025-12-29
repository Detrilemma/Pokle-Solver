# Pokle Solver - AI Agent Instructions

## Project Overview
Pokle Solver is a Python tool that solves "Pokle" games - a Wordle-style game for poker hands. It finds all possible 5-card board runouts (flop/turn/river) that satisfy specific hand ranking constraints for 3 players across the flop, turn, and river.

## Core Architecture

### Three-Class System
1. **Card** (`card.py`): Immutable playing card with rank (2-14, where 11=J, 12=Q, 13=K, 14=A) and suit ('H', 'D', 'C', 'S')
   - Comparison operators based on **rank only** (not suit)
   - Hash/equality based on **both rank and suit** (important: two cards are equal only if rank AND suit match)
   - `to_color(color)` method converts Card → ColorCard
   
2. **ColorCard** (`card.py`): Extends Card with Wordle-style color feedback ('g'=green/exact match, 'y'=yellow/partial match, 'e'=grey/no match)
   - Used for displaying guess feedback in the Pokle game
   - Hash/equality includes the color attribute
   
3. **Table** (`table.py`): Represents a poker table with 3-5 cards (flop/turn/river)
   - `flop`: frozenset of first 3 cards (unordered)
   - `turn`: 4th card or None
   - `river`: 5th card or None
   - `compare(other)` returns ColorTable showing Wordle-style matches
   
4. **ColorTable** (`table.py`): Extends Table with ColorCard objects instead of Card objects
   - `is_match(other)` validates if ColorTable could result from comparing with a given Table

5. **Solver** (`solver.py`): Main algorithm engine
   - Takes 3 players' hole cards (2 cards each) and hand ranking constraints
   - Finds all valid board runouts via combinatorial search with poker hand evaluation

### Hand Rankings Constraints
- **Critical**: Hand rankings expect integers 1-3, NOT strings "P1"-"P3"
  - 1 = best hand, 2 = second best, 3 = worst hand
  - Example: `flop_hand_ranks=[2, 1, 3]` means P2 has best hand, P1 second, P3 worst
- Validation: `sorted(hand_ranks) == [1, 2, 3]` (must be permutation)

### Wordle-Style Comparison Logic (Critical for `Table.compare()`)
**Flop (first 3 cards, unordered):**
- Green ('g'): Card matches exact rank+suit in other table's flop
- Yellow ('y'): Card matches rank OR suit (but not both) of a remaining card after greens removed
- Grey ('e'): No rank or suit match
- **Order doesn't matter**: Greens matched first, then yellows from remaining cards

**Turn/River (positional):**
- Green: Exact match at same position
- Yellow: Rank OR suit match at same position
- Grey: No match

## Performance-Critical Patterns

### NumPy Vectorization in `Table.compare()`
The `compare()` method is called **millions of times** in solver workflows:
```python
# Efficient: NumPy broadcasting for yellow/grey detection
yellow_flags = (
    (self_ranks[:, None] == other_ranks[None, :]) |
    (self_suits[:, None] == other_suits[None, :])
)
yellow_mask = np.any(yellow_flags, axis=1)
```
- Pre-allocate lists, avoid set comprehensions
- Use direct `ColorCard(rank, suit, color)` constructor, not `card.to_color(color)` in loops
- Encode suits as integers 0-3 before NumPy operations (not `ord()` characters)

### Avoid Numba
Previous attempts to use `@vectorize` decorators caused LLVM compilation crashes. Use pure NumPy broadcasting instead.

## Display Conventions

### Terminal Colors (ANSI Escape Codes)
```python
# Card.__str__() - Red/black text on white background
suit_colors = {"H": "\033[38;2;255;0;0m", "D": "\033[38;2;255;0;0m",  # Red RGB
               "C": "\033[30m", "S": "\033[30m"}  # Black
bg_color = "\033[47m"  # White background

# ColorCard.__str__() - Colored backgrounds
bg_colors = {'g': "\033[42m",              # Green
             'y': "\033[43m",              # Yellow  
             'e': "\033[48;2;160;160;160m"} # Grey RGB
```
- Suits use Unicode: ♥ ♦ ♣ ♠
- `__repr__()` returns parseable format: "AH", "10D", "KS_g"
- `__str__()` returns colored terminal output

### Immutability
- All `@property` accessors on Table/ColorTable are **read-only** (no setters)
- `_flop`, `_turn`, `_river`, `_cards` are private attributes
- Methods like `add_cards()` return **new** Table instances

## Key Solver Workflow

1. **Initialize** Solver with 3 players' hole cards + hand ranking constraints (integers 1-3 per phase)
2. **solve()**: Combinatorially filters all possible boards
   - `possible_flops()`: Find 3-card boards matching flop rankings
   - `possible_turns_rivers()`: Add 4th card matching turn rankings, then 5th for river
   - River validation: All board cards must be used in at least one player's best hand (unless flush)
3. **get_maxh_table()**: Returns the guess with highest Shannon entropy (best information gain)
4. **next_table_guess(table_colors)**: Filter possible rivers based on Wordle feedback
5. **print_game(river)**: Display formatted output with hand rankings per phase

### Entropy-Based Guessing
Uses pandas DataFrame with all possible (guess, answer) comparisons:
```python
# Pivot to comparison matrix
self.comparisons_matrix = self.table_comparisons.pivot(
    index="answer_str", columns="guess_str", values="table_comparison"
)
# Shannon entropy to find best guess
self.river_entropies = self.comparisons_matrix.apply(
    self.entropy_from_series, axis=0
).sort_values(ascending=False)
```

## Testing & Development

### Testing Strategy
- **Framework**: pytest for both unit and integration tests
- **Current state**: No formal tests yet - implementation changes in progress before test development
- **Manual testing**: Use `example()`, `sandbox()`, or `demo()` functions in `example.py`
- Test cases available in README.md for manual validation

### Running the Solver
```bash
cd src/pokle_solver
python example.py  # Runs demo() interactively
```

### Common Test Cases
See README.md for hand-crafted test scenarios with expected color outputs.

## Dependencies
- **pandas** (≥2.3.3): DataFrame operations, entropy calculations
- **scipy** (≥1.16.2): Shannon entropy via `scipy.stats.entropy`
- **numpy**: Array operations in Table.compare() for vectorized comparisons

## Coding Principles

### DRY (Don't Repeat Yourself)
Always adhere to the DRY principle - avoid code duplication by:
- Extracting common logic into helper methods or functions
- Reusing existing methods rather than reimplementing similar logic
- Using inheritance appropriately (e.g., ColorCard extends Card, ColorTable extends Table)
- Creating shared utilities for repeated operations (e.g., `__encode_cards()` in Table)

## Anti-Patterns to Avoid
1. **Don't** use strings "P1"-"P3" for hand rankings - use integers 1-3
2. **Don't** create ColorCards via `card.to_color()` in tight loops - use direct constructor
3. **Don't** try boolean array indexing on Python lists - convert to `np.array()` first
4. **Don't** assume Card equality compares only rank - it compares rank AND suit
5. **Don't** use Numba decorators - stick with NumPy
6. **Don't** modify Table attributes after construction - they're immutable by design

## Planned Improvements (from README TODO)
- Implement object pooling/caching for ColorCard creation in `compare()`
- Add comprehensive test suite
- Set up Ruff pre-commit hooks
- Add argument validation in `rank_hands()`
- Make appropriate Solver methods private
- Connect to web via Playwright for live Pokle games
