# Pokle-Solver
This project solves Pokle games

## Project Notes:
### To Do:
- Test implementing my own combination function vs itertools function
- Change GH handle to Detrilemma
- Implement Shannon entropy calculator
- Learn and implement Ruff

### Testing examples:
```
guess = [Card.from_string(c) for c in ['4S', 'KD', '7S', '4D', '6S']]
answer = [Card.from_string(c) for c in ['3H', '9D', 'KS', '6C', '4S']]

guess = [Card.from_string(c) for c in ['6D', '7D', '9C', 'KC', 'AS']]
answer = [Card.from_string(c) for c in ['9H', '3S', '6D', 'KC', '9S']]

guess = [Card.from_string(c) for c in ['KS', '9S', 'AS', '4H', '6S']]
answer = [Card.from_string(c) for c in ['7S', 'KS', 'AH', '4C', '6S']]

guess = [Card.from_string(c) for c in ['AS', 'KS', 'QS', 'JH', '10D']]
answer = [Card.from_string(c) for c in ['AS', '2D', '3C', 'JD', '10D']]

guess = [Card.from_string(c) for c in ['7H', '9S', '7S', '3D', 'KH']]
answer = [Card.from_string(c) for c in ['7S', '9S', '7H', '3H', 'KD']]

guess = [Card.from_string(c) for c in ['JD', 'JC', 'KD', '2H', '3S']]
answer = [Card.from_string(c) for c in ['JD', 'KS', 'QH', '2D', '3S']]

print(solver_1011.compare_tables(guess, answer))
```