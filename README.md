# Pokle-Solver
This project solves Pokle games

## Project Notes:
### To Do:
- ensure proper validation for the self.__tables_compared variable in the next_table_guess method.
- when there are 0 possible rivers, have the solver revert to previous list of valid rivers.
- clean up some the methods. Anytime you initialize one of the class attributes in a method, it should be returned by a separate method.
- preserve green and yellow card order in game printout.
- rewrite tests
- take out references to the table object in solver.py
- figure out git hooks to Ruff
- connect to the web with playwright

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

2:  0  1  2  3 
3:  4  5  6  7 
4:  8  9  10 11 
5:  12 13 14 15 
6:  16 17 18 19 
7:  20 21 22 23 
8:  24 25 26 27 
9:  28 29 30 31 
10: 32 33 34 35 
11: 36 37 38 39 
12: 40 41 42 43 
13: 44 45 46 47 
14: 48 49 50 51

### compare() rules description
If two cards in the same position (flop, turn, river) have the same rank and suit, they are "green". If the cards in the same position have either a matching rank or suit (but not both), they are "yellow". For the cards in the flop (the first three cards), the order of the cards does not matter. ie, 2H 3D 4S is the same as 4S 2H 3D. In the flop, two cards in the guess that match either the rank or the suit (but is not a complete match) of one card would both be "yellow". However, if one card matches both the rank and suit of one card, it is "green" and the other card would be "grey" (or not colored). For example, if the flop of the guess is 2H 3D 4S and the flop of the answer is 4D 5S 2H, the first card would be "green" (2H), the second and third card would be "yellow" (3D matches the D of 4D, and 4S matches the S of 5S). Another example, if the flop of the guess is KD KH 3D and the flop of the answer is 7C KS AS, the first and second cards would be "yellow" (KD and KH both match the K of KS), and the third card would be "grey" (3D does not match either the rank or suit of any card in the answer). Final example, if the flop of the guess is KS KH 3D and the flop of the answer is 7C KS AS, the first card would be "green" (KS), the second card would be "grey" (KH does not match either the rank or suit of any remaining cards in the answer), and the third card would be "grey" (3D does not match either the rank or suit of any remaining cards in the answer). Cards in the turn (the fourth card) and river (the fifth card) are compared by position, so the fourth card of the guess is compared to the fourth card of the answer, and the fifth card of the guess is compared to the fifth card of the answer.