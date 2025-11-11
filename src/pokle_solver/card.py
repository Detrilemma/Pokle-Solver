class Card:
    """Represents a standard playing card with rank and suit.

    A Card object represents a single playing card from a standard 52-card deck.
    Cards are immutable and hashable, making them suitable for use in sets and
    as dictionary keys.

    Attributes:
        rank (int): Card rank from 2-14 (where 11=Jack, 12=Queen, 13=King, 14=Ace)
        suit (str): Card suit, one of 'H' (Hearts), 'D' (Diamonds), 'C' (Clubs), 'S' (Spades)

    Examples:
        >>> card = Card(14, 'H')  # Ace of Hearts
        >>> card = Card.from_string('AH')  # Ace of Hearts
        >>> card = Card.from_string('10D')  # Ten of Diamonds
        >>> card = Card.from_tuple((13, 'S'))  # King of Spades
    """

    __slots__ = ("rank", "suit", "_hash")

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
        self._hash = None  # Lazy hash computation

    @classmethod
    def from_string(cls, card_string: str):
        """Create a Card from a string representation.

        Args:
            card_string (str): String like 'AH', '10D', 'KS', etc.

        Returns:
            Card: New Card instance.

        Raises:
            ValueError: If card_string is invalid or None.

        Examples:
            >>> card = Card.from_string('AH')  # Ace of Hearts
            >>> card = Card.from_string('10D')  # 10 of Diamonds
            >>> card = Card.from_string('KS')  # King of Spades
        """
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
        """Create a Card from a tuple representation.

        Args:
            card_tuple (tuple): Tuple of (rank, suit) where rank is int or str.

        Returns:
            Card: New Card instance.

        Examples:
            >>> card = Card.from_tuple((14, 'H'))  # Ace of Hearts
            >>> card = Card.from_tuple(('A', 'H'))  # Ace of Hearts
            >>> card = Card.from_tuple((10, 'D'))  # 10 of Diamonds
        """
        rank, suit = card_tuple
        if isinstance(rank, str):
            rank = cls.rank_from_string(rank)
        return cls(rank, suit)

    @staticmethod
    def rank_from_string(rank_str: str) -> int:
        """Convert a rank string to its integer value.

        Args:
            rank_str (str): Rank as string ('A', 'K', 'Q', 'J', 'T', or '2'-'10').

        Returns:
            int: Integer rank (2-14).

        Raises:
            ValueError: If rank_str is not a valid rank.

        Examples:
            >>> Card.rank_from_string('A')
            14
            >>> Card.rank_from_string('K')
            13
            >>> Card.rank_from_string('10')
            10
        """
        face_cards = {"T": 10, "J": 11, "Q": 12, "K": 13, "A": 14}
        try:
            return int(face_cards.get(rank_str, rank_str))
        except ValueError:
            raise ValueError("Rank must be an integer or a valid face card")

    def __repr__(self):
        """Return a formal string representation of the Card.

        Returns:
            str: String like "Card(rank=14, suit='H')".

        Examples:
            >>> card = Card(14, 'H')
            >>> repr(card)
            "Card(rank=14, suit='H')"
        """
        return f"Card(rank={self.rank}, suit='{self.suit}')"

    def __str__(self):
        """Return a human-readable string representation of the Card.

        Returns:
            str: String like 'AH', '10D', 'KS', or '__' for empty card.

        Examples:
            >>> card = Card(14, 'H')
            >>> str(card)
            'AH'
            >>> card = Card(10, 'D')
            >>> str(card)
            '10D'
        """
        if self.rank is None and self.suit is None:
            return "__"
        face_cards = {11: "J", 12: "Q", 13: "K", 14: "A"}
        return f"{face_cards.get(self.rank, self.rank)}{self.suit}"

    def pstr(self):
        """Return a pretty-printed colored string representation of the Card.

        Returns:
            str: ANSI colored string with card symbol and colored background.

        Examples:
            >>> card = Card(14, 'H')
            >>> card.pstr()  # Returns colored output (shown as plain text here)
            ' A♥'
        """
        if self.rank is None and self.suit is None:
            return "__"

        face_cards = {11: "J", 12: "Q", 13: "K", 14: "A"}
        suit_symbols = {"H": "♥", "D": "♦", "C": "♣", "S": "♠"}
        suit_colors = {
            "H": "\033[38;2;255;0;0m",
            "D": "\033[38;2;255;0;0m",
            "C": "\033[30m",
            "S": "\033[30m",
        }  # Red for H/D, Black for C/S

        reset_color = "\033[0m"
        rank_str = face_cards.get(self.rank, str(self.rank))
        suit_symbol = suit_symbols[self.suit]

        # Pad the visible content to 3 characters BEFORE adding color codes
        visible_str = f"{rank_str}{suit_symbol}".rjust(3)

        text_color = suit_colors[self.suit]
        bg_color = "\033[47m"

        return f"{bg_color}{text_color}{visible_str}{reset_color}"

    def __eq__(self, other):
        """Check if two Cards are equal (same rank and suit).

        Args:
            other: Object to compare with.

        Returns:
            bool: True if cards have same rank and suit, False otherwise.
            NotImplemented: If other is not a Card.

        Examples:
            >>> Card(14, 'H') == Card(14, 'H')
            True
            >>> Card(14, 'H') == Card(14, 'D')
            False
        """
        if isinstance(other, Card):
            return self.rank == other.rank and self.suit == other.suit
        return NotImplemented

    def __hash__(self):
        """Return hash of the Card for use in sets and dicts.

        Returns:
            int: Hash value based on rank and suit.

        Examples:
            >>> card = Card(14, 'H')
            >>> hash(card)  # Returns integer hash
        """
        if self._hash is None:
            self._hash = hash((self.rank, self.suit))
        return self._hash

    def __lt__(self, other):
        """Check if this Card's rank is less than another Card's rank.

        Args:
            other: Card to compare with.

        Returns:
            bool: True if this card's rank < other card's rank.
            NotImplemented: If other is not a Card.

        Examples:
            >>> Card(10, 'H') < Card(14, 'H')
            True
        """
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
        """Check if two Cards have the same suit.

        Args:
            other: Card to compare with.

        Returns:
            bool: True if both cards have the same suit.
            NotImplemented: If other is not a Card.

        Examples:
            >>> Card(10, 'H').is_same_suit(Card(14, 'H'))
            True
            >>> Card(10, 'H').is_same_suit(Card(10, 'D'))
            False
        """
        if isinstance(other, Card):
            return self.suit == other.suit
        return NotImplemented

    def is_same_rank(self, other):
        """Check if two Cards have the same rank.

        Args:
            other: Card to compare with.

        Returns:
            bool: True if both cards have the same rank.
            NotImplemented: If other is not a Card.

        Examples:
            >>> Card(10, 'H').is_same_rank(Card(10, 'D'))
            True
            >>> Card(10, 'H').is_same_rank(Card(14, 'H'))
            False
        """
        if isinstance(other, Card):
            return self.rank == other.rank
        return NotImplemented

    def to_color(self, color: str = "e"):
        """Convert this Card to a ColorCard with the specified color.

        Args:
            color (str, optional): Color code - 'g' (green), 'y' (yellow), or 'e' (grey). Defaults to 'e'.

        Returns:
            ColorCard: New ColorCard with same rank/suit and specified color.

        Raises:
            ValueError: If color not in ['g', 'y', 'e'].

        Examples:
            >>> card = Card(14, 'H')
            >>> colored = card.to_color('g')
            >>> str(colored)
            'AH_g'
        """
        if color not in ["g", "y", "e"]:
            raise ValueError(
                "Color must be one of 'g' (green), 'y' (yellow), or 'e' (grey)"
            )
        return ColorCard(self.rank, self.suit, color)


class ColorCard(Card):
    """Represents a playing card with an associated color feedback indicator.

    ColorCard extends Card by adding a color attribute used in the Pokle game
    to indicate match quality when comparing guesses to answers:
    - 'g' (green): Exact match (correct rank AND suit)
    - 'y' (yellow): Partial match (correct rank OR suit, but not both)
    - 'e' (grey/empty): No match (neither rank nor suit matches)

    This is used for providing feedback in the guessing game, similar to Wordle
    but for poker boards.

    Attributes:
        rank (int): Inherited from Card
        suit (str): Inherited from Card
        color (str): Match indicator - 'g', 'y', or 'e'

    Examples:
        >>> card = ColorCard(14, 'H', 'g')  # Green Ace of Hearts (exact match)
        >>> card = ColorCard.from_string('10D_y')  # Yellow 10 of Diamonds (partial match)
        >>> card = ColorCard.from_string('KS_e')  # Grey King of Spades (no match)
    """

    __slots__ = ("_color", "_hash_color")

    def __init__(self, rank: int = None, suit: str = None, color: str = "e"):
        super().__init__(rank, suit)
        if color not in ["g", "y", "e"]:
            raise ValueError(
                "Color must be one of 'g' (green), 'y' (yellow), or 'e' (grey)"
            )
        self._color = color
        self._hash_color = None  # Lazy hash computation

    @classmethod
    def from_string(cls, card_string: str):
        """Create a ColorCard from a string representation.

        Args:
            card_string (str): String like 'AH_g', '10D_y', or 'KS' (defaults to grey).

        Returns:
            ColorCard: New ColorCard instance.

        Examples:
            >>> card = ColorCard.from_string('AH_g')  # Green Ace of Hearts
            >>> card = ColorCard.from_string('10D_y')  # Yellow 10 of Diamonds
            >>> card = ColorCard.from_string('KS')  # Grey King of Spades (default)
        """
        if "_" in card_string:
            card_part, color_part = card_string.split("_")
            base_card = super().from_string(card_part)
            return cls(base_card.rank, base_card.suit, color_part)
        else:
            base_card = super().from_string(card_string)
            return cls(base_card.rank, base_card.suit, "e")

    @classmethod
    def from_tuple(cls, card_tuple: tuple):
        """Create a ColorCard from a tuple representation.

        Args:
            card_tuple (tuple): Tuple of (rank, suit) or (rank, suit, color).

        Returns:
            ColorCard: New ColorCard instance.

        Raises:
            ValueError: If tuple length is not 2 or 3.

        Examples:
            >>> card = ColorCard.from_tuple((14, 'H', 'g'))  # Green Ace
            >>> card = ColorCard.from_tuple((10, 'D'))  # Grey 10 (default)
        """
        if len(card_tuple) == 3:
            rank, suit, color = card_tuple
        elif len(card_tuple) == 2:
            rank, suit = card_tuple
            color = "e"
        else:
            raise ValueError(
                "Tuple must be of the form (rank, suit) or (rank, suit, color)"
            )

        if isinstance(rank, str):
            rank = cls.rank_from_string(rank)
        return cls(rank, suit, color)

    def __repr__(self):
        """Return a formal string representation of the ColorCard.

        Returns:
            str: String like "ColorCard(rank=14, suit='H', color='g')".

        Examples:
            >>> card = ColorCard(14, 'H', 'g')
            >>> repr(card)
            "ColorCard(rank=14, suit='H', color='g')"
        """
        return f"ColorCard(rank={self.rank}, suit='{self.suit}', color='{self.color}')"

    def __str__(self):
        """Return a human-readable string representation of the ColorCard.

        Returns:
            str: String like 'AH_g', '10D_y', or 'KS_e'.

        Examples:
            >>> card = ColorCard(14, 'H', 'g')
            >>> str(card)
            'AH_g'
        """
        return super().__str__() + f"_{self.color}"

    def pstr(self):
        """Return a pretty-printed colored string with background color.

        Returns:
            str: ANSI colored string with color-coded background.

        Examples:
            >>> card = ColorCard(14, 'H', 'g')
            >>> card.pstr()  # Returns colored output with green background
        """
        base_str = super().pstr()
        bg_colors = {
            "g": "\033[42m",  # Green background
            "y": "\033[43m",  # Yellow background
            "e": "\033[48;2;160;160;160m",  # Light grey RGB background
        }
        bg_color = bg_colors[self.color]
        return base_str.replace("\033[47m", bg_color)

    @property
    def color(self) -> str:
        """Get the color of the card.

        Returns:
            str: Card color ('g', 'y', or 'e').

        Examples:
            >>> card = ColorCard(14, 'H', 'g')
            >>> card.color
            'g'
        """
        return self._color

    @color.setter
    def color(self, value: str):
        """Set the color of the card.

        Args:
            value (str): Card color ('g' for green, 'y' for yellow, 'e' for grey).

        Raises:
            ValueError: If value is not 'g', 'y', or 'e'.

        Examples:
            >>> card = ColorCard(14, 'H', 'g')
            >>> card.color = 'y'
            >>> card.color
            'y'
        """
        if value not in ["g", "y", "e"]:
            raise ValueError(
                "Color must be one of 'g' (green), 'y' (yellow), or 'e' (grey)"
            )
        self._color = value

    def __hash__(self):
        """Compute hash value for the ColorCard.

        Returns:
            int: Hash value based on rank, suit, and color.

        Examples:
            >>> card = ColorCard(14, 'H', 'g')
            >>> hash(card)  # Returns consistent hash value
        """
        if self._hash_color is None:
            self._hash_color = hash((self.rank, self.suit, self.color))
        return self._hash_color

    def __eq__(self, other):
        """Check if two ColorCards are equal.

        Args:
            other: Object to compare with.

        Returns:
            bool: True if rank, suit, and color match.
            NotImplemented: If other is not a ColorCard.

        Examples:
            >>> ColorCard(14, 'H', 'g') == ColorCard(14, 'H', 'g')
            True
            >>> ColorCard(14, 'H', 'g') == ColorCard(14, 'H', 'y')
            False
        """
        if isinstance(other, ColorCard):
            return (
                self.rank == other.rank
                and self.suit == other.suit
                and self.color == other.color
            )
        return NotImplemented

    def __ne__(self, other):
        """Check if two ColorCards are not equal.

        Args:
            other: Object to compare with.

        Returns:
            bool: True if rank, suit, or color differ.
            NotImplemented: If other is not a ColorCard.

        Examples:
            >>> ColorCard(14, 'H', 'g') != ColorCard(14, 'H', 'y')
            True
            >>> ColorCard(14, 'H', 'g') != ColorCard(14, 'H', 'g')
            False
        """
        if isinstance(other, ColorCard):
            return (
                self.rank != other.rank
                or self.suit != other.suit
                or self.color != other.color
            )
        return NotImplemented

    def is_same_color(self, other):
        """Check if two ColorCards have the same color.

        Args:
            other: ColorCard to compare with.

        Returns:
            bool: True if both cards have the same color.
            NotImplemented: If other is not a ColorCard.

        Examples:
            >>> ColorCard(14, 'H', 'g').is_same_color(ColorCard(10, 'D', 'g'))
            True
            >>> ColorCard(14, 'H', 'g').is_same_color(ColorCard(14, 'H', 'y'))
            False
        """
        if isinstance(other, ColorCard):
            return self.color == other.color
        return NotImplemented
