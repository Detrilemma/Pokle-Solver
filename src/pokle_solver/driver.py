from card import Card

card1 = Card.from_string("2H")
card2 = Card.from_string("AS")
card3 = Card.from_string("4D")
print(card1, card2, card3)
print(hash(card1), hash(card2), hash(card3))