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

    __slots__ = ("_rank", "_suit", "_hash", "_card_index")
    # Class-level cache for card indices (max 52 entries)
    _card_index_cache = {}
    _suit_indices = {"C": 0, "D": 1, "H": 2, "S": 3}

    def __init__(self, rank: int | None = None, suit: str | None = None):
        has_rank_and_suit = rank is not None and suit is not None
        if has_rank_and_suit:
            assert rank is not None and suit is not None  # Type narrowing
            if rank < 2 or rank > 14:
                raise ValueError(
                    "Rank must be between 2 and 14 (where 11=J, 12=Q, 13=K, 14=A)"
                )
            assert rank is not None and suit is not None  # Type narrowing for cache operations
            cache_key = (rank, suit)
            if cache_key not in Card._card_index_cache:
                Card._card_index_cache[cache_key] = (rank - 2) * 4 + Card._suit_indices[suit]
            self._card_index = Card._card_index_cache[cache_key]
            if suit not in ["H", "D", "C", "S"]:
                raise ValueError("Suit must be one of 'H', 'D', 'C', 'S'")
        else:
            self._card_index = None

        self._rank = rank
        self._suit = suit
        self._hash = None  # Lazy hash computation
        # Use cached card_index or compute and cache it

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

    @property
    def rank(self) -> int | None:
        """Get the rank of the card.
        
        Returns:
            int: Card rank from 2-14 (where 11=Jack, 12=Queen, 13=King, 14=Ace)
        """
        return self._rank

    @property
    def suit(self) -> str | None:
        """Get the suit of the card.
        
        Returns:
            str: Card suit, one of 'H' (Hearts), 'D' (Diamonds), 'C' (Clubs), 'S' (Spades)
        """
        return self._suit

    @property
    def card_index(self) -> int | None:
        """Get the card index (0-51) for this card.
        
        Returns:
            int: Card index in the range 0-51, or None if card has no rank/suit
        """
        return self._card_index

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
        return f"Card(rank={self._rank}, suit='{self._suit}')"

    def __str__(self):
        if self._rank is None and self._suit is None:
            return "__"
        face_cards = {11: "J", 12: "Q", 13: "K", 14: "A"}
        assert self._rank is not None and self._suit is not None
        return f"{face_cards.get(self._rank, self._rank)}{self._suit}"

    def pstr(self):
        """Return a pretty-printed colored string representation of the Card.

        Returns:
            str: ANSI colored string with card symbol and colored background.

        Examples:
            >>> card = Card(14, 'H')
            >>> card.pstr()  # Returns colored output (shown as plain text here)
            ' A♥'
        """
        if self._rank is None and self._suit is None:
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
        assert self._rank is not None and self._suit is not None
        rank_str = face_cards.get(self._rank, str(self._rank))
        suit_symbol = suit_symbols[self._suit]

        # Pad the visible content to 3 characters BEFORE adding color codes
        visible_str = f"{rank_str}{suit_symbol}".rjust(3)

        text_color = suit_colors[self._suit]
        bg_color = "\033[47m"

        return f"{bg_color}{text_color}{visible_str}{reset_color}"

    def __eq__(self, other):
        if isinstance(other, Card):
            return self._rank == other._rank and self._suit == other._suit
        return NotImplemented

    def __hash__(self):
        if self._hash is None:
            self._hash = hash((self._rank, self._suit))
        return self._hash

    def __lt__(self, other):
        if isinstance(other, Card):
            if self._rank is None or other._rank is None:
                return NotImplemented
            return self._rank < other._rank
    def __le__(self, other):
        if isinstance(other, Card):
            if self._rank is None or other._rank is None:
                return NotImplemented
            return self._rank <= other._rank
    def __gt__(self, other):
        if isinstance(other, Card):
            if self._rank is None or other._rank is None:
                return NotImplemented
            return self._rank > other._rank
    def __ge__(self, other):
        if isinstance(other, Card):
            if self._rank is None or other._rank is None:
                return NotImplemented
            return self._rank >= other._rank
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, Card):
            return self._rank != other._rank or self._suit != other._suit
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
            return self._suit == other._suit
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
            return self._rank == other._rank
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
        return ColorCard(self._rank, self._suit, color)


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

    def __init__(self, rank: int | None = None, suit: str | None = None, color: str = "e"):
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
        return f"ColorCard(rank={self._rank}, suit='{self._suit}', color='{self.color}')"

    def __str__(self):
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
        return self._color

    @color.setter
    def color(self, value: str):
        if value not in ["g", "y", "e"]:
            raise ValueError(
                "Color must be one of 'g' (green), 'y' (yellow), or 'e' (grey)"
            )
        self._color = value

    def __hash__(self):
        if self._hash_color is None:
            self._hash_color = hash((self._rank, self._suit, self.color))
        return self._hash_color

    def __eq__(self, other):
        if isinstance(other, ColorCard):
            return (
                self._rank == other._rank
                and self._suit == other._suit
                and self._color == other._color
            )
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, ColorCard):
            return (
                self._rank != other._rank
                or self._suit != other._suit
                or self._color != other._color
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
            return self._color == other._color
        return NotImplemented
