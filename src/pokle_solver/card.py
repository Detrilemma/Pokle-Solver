class Card:
    def __init__(self, rank: int = None, suit: str = None):
        has_rank_and_suit = rank is not None and suit is not None
        if has_rank_and_suit and (rank < 2 or rank > 14):
            raise ValueError(
            "Rank must be between 2 and 14 (where 11=J, 12=Q, 13=K, 14=A)"
            )
        if has_rank_and_suit and suit not in ["H", "D", "C", "S"]:
            raise ValueError("Suit must be one of 'H', 'D', 'C', 'S'")

        self.rank = rank
        self.suit = suit

    @classmethod
    def from_string(cls, card_string: str):
        """Create card from string like '10H' or 'AS'"""
        if card_string is None:
            raise ValueError("card_string must be provided")
        s = card_string.strip().upper()
        if len(s) < 2 or len(s) > 3:
            raise ValueError(f"Invalid card string: {card_string}")
        rank = cls.rank_from_string(s[:-1])
        suit = s[-1]
        return cls(rank, suit)

    @classmethod
    def from_tuple(cls, card_tuple: tuple):
        """Create card from tuple like (10, 'H')"""
        rank, suit = card_tuple
        if isinstance(rank, str):
            rank = cls.rank_from_string(rank)
        return cls(rank, suit)
    
    @staticmethod
    def rank_from_string(rank_str: str) -> int:
        face_cards = {"T": 10, "J": 11, "Q": 12, "K": 13, "A": 14}
        try:
            return int(face_cards.get(rank_str, rank_str))
        except ValueError:
            raise ValueError("Rank must be an integer or a valid face card")

    def __repr__(self):
        return f"Card(rank={self.rank}, suit='{self.suit}')"

    def __str__(self):
        if self.rank is None and self.suit is None:
            return "__"
        face_cards = {11: "J", 12: "Q", 13: "K", 14: "A"}
        return f"{face_cards.get(self.rank, self.rank)}{self.suit}"

    def pstr(self):
        if self.rank is None and self.suit is None:
            return "__"

        face_cards = {11: "J", 12: "Q", 13: "K", 14: "A"}
        suit_symbols = {"H": "♥", "D": "♦", "C": "♣", "S": "♠"}
        suit_colors = {"H": "\033[38;2;255;0;0m", "D": "\033[38;2;255;0;0m", "C": "\033[30m", "S": "\033[30m"}  # Red for H/D, Black for C/S

        reset_color = "\033[0m"
        rank_str = face_cards.get(self.rank, str(self.rank))
        suit_symbol = suit_symbols[self.suit]
        
        # Pad the visible content to 3 characters BEFORE adding color codes
        visible_str = f"{rank_str}{suit_symbol}".rjust(3)
        
        text_color = suit_colors[self.suit]
        bg_color = "\033[47m"
        
        return f"{bg_color}{text_color}{visible_str}{reset_color}"

    def __eq__(self, other):
        if isinstance(other, Card):
            return self.rank == other.rank and self.suit == other.suit
        return NotImplemented

    def __hash__(self):
        return hash((self.rank, self.suit))

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
            return self.rank != other.rank or self.suit != other.suit
        return NotImplemented

    def is_same_suit(self, other):
        if isinstance(other, Card):
            return self.suit == other.suit
        return NotImplemented

    def is_same_rank(self, other):
        if isinstance(other, Card):
            return self.rank == other.rank
        return NotImplemented

    def to_color(self, color: str = 'e'):
        """Convert a Card to a ColorCard with the specified color."""
        if color not in ['g', 'y', 'e']:
            raise ValueError("Color must be one of 'g' (green), 'y' (yellow), or 'e' (grey)")
        return ColorCard(self.rank, self.suit, color)

class ColorCard(Card):
    def __init__(self, rank: int = None, suit: str = None, color: str = 'e'):
        super().__init__(rank, suit)
        if color not in ['g', 'y', 'e']:
            raise ValueError("Color must be one of 'g' (green), 'y' (yellow), or 'e' (grey)")
        self._color = color

    @classmethod
    def from_string(cls, card_string: str):
        '''Create ColorCard from string like '10H_g' or 'AS_y' '''
        if '_' in card_string:
            card_part, color_part = card_string.split('_')
            base_card = super().from_string(card_part)
            return cls(base_card.rank, base_card.suit, color_part)
        else:
            base_card = super().from_string(card_string)
            return cls(base_card.rank, base_card.suit, 'e')
        
    @classmethod
    def from_tuple(cls, card_tuple: tuple):
        '''Create ColorCard from tuple like (10, 'H', 'g')'''
        if len(card_tuple) == 3:
            rank, suit, color = card_tuple
        elif len(card_tuple) == 2:
            rank, suit = card_tuple
            color = 'e'
        else:
            raise ValueError("Tuple must be of the form (rank, suit) or (rank, suit, color)")
        
        if isinstance(rank, str):
            rank = cls.rank_from_string(rank)
        return cls(rank, suit, color)

    def __repr__(self):
        return f"ColorCard(rank={self.rank}, suit='{self.suit}', color='{self.color}')"

    def __str__(self):
        return super().__str__() + f"_{self.color}"

    def pstr(self):
        base_str = super().pstr()
        bg_colors = {
            'g': "\033[42m",  # Green background
            'y': "\033[43m",  # Yellow background
            'e': "\033[48;2;160;160;160m"   # Light grey RGB background
        }
        bg_color = bg_colors[self.color]
        return base_str.replace("\033[47m", bg_color)

    @property
    def color(self) -> str:
        return self._color

    @color.setter
    def color(self, value: str):
        if value not in ['g', 'y', 'e']:
            raise ValueError("Color must be one of 'g' (green), 'y' (yellow), or 'e' (grey)")
        self._color = value

    def __hash__(self):
        return hash((self.rank, self.suit, self.color))
    
    def __eq__(self, other):
        if isinstance(other, ColorCard):
            return (self.rank == other.rank and 
                    self.suit == other.suit and 
                    self.color == other.color)
        return NotImplemented
    
    def __ne__(self, other):
        if isinstance(other, ColorCard):
            return (self.rank != other.rank or 
                    self.suit != other.suit or 
                    self.color != other.color)
        return NotImplemented
    
    def is_same_color(self, other):
        if isinstance(other, ColorCard):
            return self.color == other.color
        return NotImplemented
    
c = Card.from_string("10H")
cc = c.to_color('g')