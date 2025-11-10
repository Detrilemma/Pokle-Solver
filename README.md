# Pokle-Solver
This project solves Pokle games

## Project Notes:
### To Do:
- Hot tip from Sonnet 4.5 in the compare() method: "For even more performance, consider caching ColorCard objects or using object pooling if you're calling this millions of times."
💡 FURTHER OPTIMIZATION IDEAS:
  • Consider Cython/numba for hot paths like rank_hand()
  • Parallelize solve() phases (flop/turn/river evaluation)
- proper docstrings
- Test implementing my own combination function vs itertools function
- test making the Table.compare() method more readable
- Change GH handle to Detrilemma
- figure out git hooks to Ruff
- connect to the web with playwright

Optimize rank_hand() internals (125s → ~90s potential)
27M len() calls, 16M append() calls, 9.5M hash lookups
Reduce temporary list/dict creation
Cache intermediate results within the function
Use more efficient data structures (arrays vs lists for counting)

Reduce Table.__init__() overhead (11s from add_cards)
397K Table objects created during phase search
Could use object pooling or faster construction
Avoid redundant validation for known-good inputs

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

## Notes

### compare_tables() rules description
If two cards in the same position (flop, turn, river) have the same rank and suit, they are "green". If the cards in the same position have either a matching rank or suit (but not both), they are "yellow". For the cards in the flop (the first three cards), the order of the cards does not matter. ie, 2H 3D 4S is the same as 4S 2H 3D. In the flop, two cards in the guess that match either the rank or the suit (but is not a complete match) of one card would both be "yellow". However, if one card matches both the rank and suit of one card, it is "green" and the other card would be "grey" (or not colored). For example, if the flop of the guess is 2H 3D 4S and the flop of the answer is 4D 5S 2H, the first card would be "green" (2H), the second and third card would be "yellow" (3D matches the D of 4D, and 4S matches the S of 5S). Another example, if the flop of the guess is KD KH 3D and the flop of the answer is 7C KS AS, the first and second cards would be "yellow" (KD and KH both match the K of KS), and the third card would be "grey" (3D does not match either the rank or suit of any card in the answer). Final example, if the flop of the guess is KS KH 3D and the flop of the answer is 7C KS AS, the first card would be "green" (KS), the second card would be "grey" (KH does not match either the rank or suit of any remaining cards in the answer), and the third card would be "grey" (3D does not match either the rank or suit of any remaining cards in the answer). Cards in the turn (the fourth card) and river (the fifth card) are compared by position, so the fourth card of the guess is compared to the fourth card of the answer, and the fifth card of the guess is compared to the fifth card of the answer.