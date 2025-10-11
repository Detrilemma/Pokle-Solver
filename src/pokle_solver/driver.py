from card import Card

card1 = Card.from_string("2H")
card2 = Card.from_string("AS")
card3 = Card.from_string("4D")
print(sorted([card1, card2, card3]))