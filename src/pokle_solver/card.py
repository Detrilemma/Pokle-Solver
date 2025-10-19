class Card:
    def __init__(self, rank: int = None, suit: str = None):
        face_cards = {'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        if rank != None and suit != None:
            rank = int(face_cards.get(rank, rank))
            if (rank < 2 or rank > 14):
                raise ValueError("Rank must be between 2 and 14 (where 11=J, 12=Q, 13=K, 14=A)")
            if suit not in ['H', 'D', 'C', 'S']:
                raise ValueError("Suit must be one of 'H', 'D', 'C', 'S'")
        
        self.rank = rank
        self.suit = suit

    @classmethod
    def from_string(cls, card_string: str):
        """Create card from string like '10H' or 'AS'"""
        rank = card_string[:-1]
        suit = card_string[-1]
        return cls(rank, suit)
    
    @classmethod
    def from_tuple(cls, card_tuple: tuple):
        """Create card from tuple like (10, 'H')"""
        rank, suit = card_tuple
        return cls(rank, suit)

    def __repr__(self):
        if self.rank == None and self.suit == None:
            return "C()"

        face_cards = {11: 'J', 12: 'Q', 13: 'K', 14: 'A'}
        rank_str = face_cards.get(self.rank, str(self.rank))
        return f"{rank_str}{self.suit}"

    def __eq__(self, other):
        if isinstance(other, Card):
            return self.rank == other.rank
        return NotImplemented
    
    def __lt__(self, other):
        if isinstance(other, Card):
            return self.rank < other.rank
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, Card):
            return self.rank <= other.rank
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, Card):
            return self.rank > other.rank
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, Card):
            return self.rank >= other.rank
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, Card):
            return self.rank != other.rank
        return NotImplemented
    
    def __add__(self, other):
        if isinstance(other, Card):
            return self.rank + other.rank
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Card):
            return self.rank - other.rank
        return NotImplemented

    def is_same_suit(self, other):
        if isinstance(other, Card):
            return self.suit == other.suit
        return NotImplemented

    def __hash__(self):
        suit_dict = {'H': 0, 'D': 1, 'C': 2, 'S': 3}
        return (self.rank - 2) * 4 + suit_dict[self.suit]