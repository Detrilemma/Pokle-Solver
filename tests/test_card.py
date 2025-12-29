"""Unit tests for the Card and ColorCard classes."""

import pytest

from pokle_solver.card import Card, ColorCard  # type: ignore


class TestCardInitialization:
    """Test Card class initialization and validation."""

    def test_init_with_valid_rank_and_suit(self):
        """Test creating a card with valid rank and suit."""
        card = Card(14, "H")
        assert card.rank == 14
        assert card.suit == "H"
        assert card.card_index is not None

    def test_init_with_all_valid_ranks(self):
        """Test that all ranks from 2-14 are valid."""
        for rank in range(2, 15):
            card = Card(rank, "H")
            assert card.rank == rank

    def test_init_with_all_valid_suits(self):
        """Test that all four suits are valid."""
        for suit in ["H", "D", "C", "S"]:
            card = Card(10, suit)
            assert card.suit == suit

    def test_init_with_invalid_rank_too_low(self):
        """Test that rank < 2 raises ValueError."""
        with pytest.raises(ValueError, match="Rank must be between"):
            Card(1, "H")

    def test_init_with_invalid_rank_too_high(self):
        """Test that rank > 14 raises ValueError."""
        with pytest.raises(ValueError, match="Rank must be between"):
            Card(15, "H")

    def test_init_with_invalid_suit(self):
        """Test that invalid suit raises KeyError."""
        with pytest.raises(KeyError):
            Card(10, "X")

    def test_init_with_none_values(self):
        """Test creating a card with None rank and suit (placeholder card)."""
        card = Card()
        assert card.rank is None
        assert card.suit is None
        assert card.card_index is None

    def test_card_index_caching(self):
        """Test that card_index is cached and consistent."""
        card1 = Card(10, "H")
        card2 = Card(10, "H")
        assert card1.card_index == card2.card_index

    def test_card_index_unique_for_different_cards(self):
        """Test that different cards have different card_index values."""
        card1 = Card(10, "H")
        card2 = Card(10, "D")
        card3 = Card(9, "H")
        assert card1.card_index != card2.card_index
        assert card1.card_index != card3.card_index

    def test_card_index_range(self):
        """Test that card_index is in valid range 0-51."""
        for rank in range(2, 15):
            for suit in ["C", "D", "H", "S"]:
                card = Card(rank, suit)
                assert 0 <= card.card_index <= 51  # type: ignore[operator]


class TestCardFactoryMethods:
    """Test Card factory methods for creating cards from strings and tuples."""

    def test_from_string_ace_of_hearts(self):
        """Test creating Ace of Hearts from string."""
        card = Card.from_string("AH")
        assert card.rank == 14
        assert card.suit == "H"

    def test_from_string_ten_of_diamonds(self):
        """Test creating 10 of Diamonds from string."""
        card = Card.from_string("10D")
        assert card.rank == 10
        assert card.suit == "D"

    def test_from_string_face_cards(self):
        """Test creating face cards from strings."""
        jack = Card.from_string("JC")
        queen = Card.from_string("QS")
        king = Card.from_string("KH")

        assert jack.rank == 11
        assert queen.rank == 12
        assert king.rank == 13

    def test_from_string_lowercase(self):
        """Test that from_string handles lowercase input."""
        card = Card.from_string("ah")
        assert card.rank == 14
        assert card.suit == "H"

    def test_from_string_with_whitespace(self):
        """Test that from_string handles whitespace."""
        card = Card.from_string("  KS  ")
        assert card.rank == 13
        assert card.suit == "S"

    def test_from_string_with_none(self):
        """Test that from_string raises ValueError with None."""
        with pytest.raises(ValueError):
            Card.from_string(None)  # type: ignore[arg-type]

    def test_from_string_with_invalid_format(self):
        """Test that from_string raises ValueError with invalid format."""
        with pytest.raises(ValueError):
            Card.from_string("A")  # Too short
        with pytest.raises(ValueError):
            Card.from_string("ABCD")  # Too long

    def test_from_tuple_with_int_rank(self):
        """Test creating card from tuple with integer rank."""
        card = Card.from_tuple((14, "H"))
        assert card.rank == 14
        assert card.suit == "H"

    def test_from_tuple_with_string_rank(self):
        """Test creating card from tuple with string rank."""
        card = Card.from_tuple(("A", "H"))
        assert card.rank == 14
        assert card.suit == "H"

    def test_rank_from_string_all_face_cards(self):
        """Test rank_from_string with all face cards."""
        assert Card.rank_from_string("T") == 10
        assert Card.rank_from_string("J") == 11
        assert Card.rank_from_string("Q") == 12
        assert Card.rank_from_string("K") == 13
        assert Card.rank_from_string("A") == 14

    def test_rank_from_string_numeric(self):
        """Test rank_from_string with numeric values."""
        assert Card.rank_from_string("2") == 2
        assert Card.rank_from_string("10") == 10

    def test_rank_from_string_invalid(self):
        """Test rank_from_string raises ValueError with invalid input."""
        with pytest.raises(ValueError):
            Card.rank_from_string("X")


class TestCardProperties:
    """Test Card property accessors."""

    def test_rank_property(self):
        """Test rank property returns correct value."""
        card = Card(13, "S")
        assert card.rank == 13

    def test_suit_property(self):
        """Test suit property returns correct value."""
        card = Card(13, "S")
        assert card.suit == "S"

    def test_card_index_property(self):
        """Test card_index property returns correct value."""
        card = Card(2, "C")
        assert card.card_index == 0  # First card in deck

    def test_card_index_calculation(self):
        """Test card_index calculation formula: (rank-2)*4 + suit_index."""
        # 2C should be 0, 2D should be 1, 2H should be 2, 2S should be 3
        assert Card(2, "C").card_index == 0
        assert Card(2, "D").card_index == 1
        assert Card(2, "H").card_index == 2
        assert Card(2, "S").card_index == 3

        # AC should be 48, AD should be 49, AH should be 50, AS should be 51
        assert Card(14, "C").card_index == 48
        assert Card(14, "D").card_index == 49
        assert Card(14, "H").card_index == 50
        assert Card(14, "S").card_index == 51


class TestCardComparison:
    """Test Card comparison operators and hash consistency."""

    def test_equality_same_rank_and_suit(self):
        """Test that cards with same rank and suit are equal."""
        card1 = Card(10, "H")
        card2 = Card(10, "H")
        assert card1 == card2

    def test_equality_different_rank(self):
        """Test that cards with different ranks are not equal."""
        card1 = Card(10, "H")
        card2 = Card(9, "H")
        assert card1 != card2

    def test_equality_different_suit(self):
        """Test that cards with different suits are not equal."""
        card1 = Card(10, "H")
        card2 = Card(10, "D")
        assert card1 != card2

    def test_less_than_by_rank(self):
        """Test less than comparison based on rank."""
        card1 = Card(9, "H")
        card2 = Card(10, "H")
        assert card1 < card2

    def test_less_than_or_equal(self):
        """Test less than or equal comparison."""
        card1 = Card(9, "H")
        card2 = Card(10, "H")
        card3 = Card(9, "D")
        assert card1 <= card2
        assert card1 <= card3

    def test_greater_than_by_rank(self):
        """Test greater than comparison based on rank."""
        card1 = Card(10, "H")
        card2 = Card(9, "H")
        assert card1 > card2

    def test_greater_than_or_equal(self):
        """Test greater than or equal comparison."""
        card1 = Card(10, "H")
        card2 = Card(9, "H")
        card3 = Card(10, "D")
        assert card1 >= card2
        assert card1 >= card3

    def test_comparison_ignores_suit(self):
        """Test that comparison operators only consider rank, not suit."""
        card1 = Card(10, "H")
        card2 = Card(10, "D")
        assert not (card1 < card2)
        assert not (card1 > card2)
        assert card1 <= card2
        assert card1 >= card2

    def test_comparison_with_none_ranks(self):
        """Test that comparison with None ranks raises TypeError."""
        card1 = Card()  # None rank
        card2 = Card(10, "H")
        with pytest.raises(TypeError):
            _ = card1 < card2  # type: ignore[operator]

    def test_hash_consistency_with_equality(self):
        """Test that equal cards have the same hash."""
        card1 = Card(10, "H")
        card2 = Card(10, "H")
        assert card1 == card2
        assert hash(card1) == hash(card2)

    def test_hash_different_for_different_cards(self):
        """Test that different cards have different hashes."""
        card1 = Card(10, "H")
        card2 = Card(10, "D")
        assert card1 != card2
        assert hash(card1) != hash(card2)

    def test_card_usable_in_set(self):
        """Test that cards can be used in sets (hashable)."""
        card1 = Card(10, "H")
        card2 = Card(10, "D")
        card3 = Card(10, "H")  # Duplicate of card1

        card_set = {card1, card2, card3}
        assert len(card_set) == 2  # card3 is duplicate of card1

    def test_card_usable_as_dict_key(self):
        """Test that cards can be used as dictionary keys."""
        card1 = Card(10, "H")
        card2 = Card(10, "D")

        card_dict = {card1: "first", card2: "second"}
        assert card_dict[card1] == "first"
        assert card_dict[Card(10, "H")] == "first"  # Same card


class TestCardHelperMethods:
    """Test Card helper methods."""

    def test_is_same_suit_true(self):
        """Test is_same_suit returns True for same suit."""
        card1 = Card(10, "H")
        card2 = Card(14, "H")
        assert card1.is_same_suit(card2) is True

    def test_is_same_suit_false(self):
        """Test is_same_suit returns False for different suits."""
        card1 = Card(10, "H")
        card2 = Card(10, "D")
        assert card1.is_same_suit(card2) is False

    def test_is_same_rank_true(self):
        """Test is_same_rank returns True for same rank."""
        card1 = Card(10, "H")
        card2 = Card(10, "D")
        assert card1.is_same_rank(card2) is True

    def test_is_same_rank_false(self):
        """Test is_same_rank returns False for different ranks."""
        card1 = Card(10, "H")
        card2 = Card(14, "H")
        assert card1.is_same_rank(card2) is False

    def test_to_color_creates_color_card(self):
        """Test to_color creates a ColorCard instance."""
        card = Card(10, "H")
        color_card = card.to_color("g")
        assert isinstance(color_card, ColorCard)
        assert color_card.rank == 10
        assert color_card.suit == "H"
        assert color_card.color == "g"

    def test_to_color_all_colors(self):
        """Test to_color with all valid color values."""
        card = Card(10, "H")
        green = card.to_color("g")
        yellow = card.to_color("y")
        grey = card.to_color("e")

        assert green.color == "g"
        assert yellow.color == "y"
        assert grey.color == "e"

    def test_to_color_default_is_grey(self):
        """Test to_color defaults to grey."""
        card = Card(10, "H")
        color_card = card.to_color()
        assert color_card.color == "e"

    def test_to_color_invalid_color(self):
        """Test to_color raises ValueError with invalid color."""
        card = Card(10, "H")
        with pytest.raises(ValueError, match="Color must be one of"):
            card.to_color("x")  # type: ignore[arg-type]


class TestCardStringRepresentation:
    """Test Card string representation methods."""

    def test_str_ace(self):
        """Test string representation of Ace."""
        card = Card(14, "H")
        assert str(card) == "AH"

    def test_str_king(self):
        """Test string representation of King."""
        card = Card(13, "S")
        assert str(card) == "KS"

    def test_str_queen(self):
        """Test string representation of Queen."""
        card = Card(12, "D")
        assert str(card) == "QD"

    def test_str_jack(self):
        """Test string representation of Jack."""
        card = Card(11, "C")
        assert str(card) == "JC"

    def test_str_ten(self):
        """Test string representation of 10."""
        card = Card(10, "H")
        assert str(card) == "10H"

    def test_str_numeric_card(self):
        """Test string representation of numeric cards."""
        card = Card(7, "D")
        assert str(card) == "7D"

    def test_str_none_card(self):
        """Test string representation of None card."""
        card = Card()
        assert str(card) == "__"

    def test_repr(self):
        """Test repr representation."""
        card = Card(10, "H")
        assert repr(card) == "Card(rank=10, suit='H')"

    def test_repr_none_card(self):
        """Test repr of None card."""
        card = Card()
        assert repr(card) == "Card(rank=None, suit='None')"

    def test_pstr_contains_ansi_codes(self):
        """Test pstr returns string with ANSI color codes."""
        card = Card(14, "H")
        pstr = card.pstr()
        assert "\033[" in pstr  # Contains ANSI escape codes
        assert "A♥" in pstr or "A" in pstr  # Contains card representation

    def test_pstr_none_card(self):
        """Test pstr for None card returns placeholder."""
        card = Card()
        assert card.pstr() == "__"


class TestColorCard:
    """Test ColorCard class functionality."""

    def test_colorcard_init_with_color(self):
        """Test creating ColorCard with color parameter."""
        card = ColorCard(10, "H", "g")
        assert card.rank == 10
        assert card.suit == "H"
        assert card.color == "g"

    def test_colorcard_init_default_color(self):
        """Test ColorCard defaults to grey color."""
        card = ColorCard(10, "H")
        assert card.color == "e"

    def test_colorcard_init_invalid_color(self):
        """Test ColorCard raises ValueError with invalid color."""
        with pytest.raises(ValueError, match="Color must be one of"):
            ColorCard(10, "H", "x")  # type: ignore[arg-type]

    def test_colorcard_from_string_with_color(self):
        """Test creating ColorCard from string with color suffix."""
        card = ColorCard.from_string("AH_g")
        assert card.rank == 14
        assert card.suit == "H"
        assert card.color == "g"

    def test_colorcard_from_string_all_colors(self):
        """Test ColorCard.from_string with all color values."""
        green = ColorCard.from_string("10D_g")
        yellow = ColorCard.from_string("10D_y")
        grey = ColorCard.from_string("10D_e")

        assert green.color == "g"
        assert yellow.color == "y"
        assert grey.color == "e"

    def test_colorcard_from_tuple(self):
        """Test creating ColorCard from tuple."""
        card = ColorCard.from_tuple((14, "H", "g"))
        assert card.rank == 14
        assert card.suit == "H"
        assert card.color == "g"

    def test_colorcard_color_property(self):
        """Test ColorCard color property getter."""
        card = ColorCard(10, "H", "g")
        assert card.color == "g"

    def test_colorcard_color_setter(self):
        """Test ColorCard color property setter."""
        card = ColorCard(10, "H", "g")
        card.color = "y"
        assert card.color == "y"

    def test_colorcard_color_setter_invalid(self):
        """Test ColorCard color setter raises ValueError with invalid color."""
        card = ColorCard(10, "H", "g")
        with pytest.raises(ValueError, match="Color must be one of"):
            card.color = "x"  # type: ignore[assignment]

    def test_colorcard_str_includes_color(self):
        """Test ColorCard string representation includes color."""
        card = ColorCard(10, "H", "g")
        assert str(card) == "10H_g"

    def test_colorcard_repr(self):
        """Test ColorCard repr."""
        card = ColorCard(10, "H", "g")
        assert repr(card) == "ColorCard(rank=10, suit='H', color='g')"

    def test_colorcard_equality_requires_same_color(self):
        """Test ColorCard equality requires same color."""
        card1 = ColorCard(10, "H", "g")
        card2 = ColorCard(10, "H", "g")
        card3 = ColorCard(10, "H", "y")

        assert card1 == card2
        assert card1 != card3

    def test_colorcard_hash_includes_color(self):
        """Test ColorCard hash includes color."""
        card1 = ColorCard(10, "H", "g")
        card2 = ColorCard(10, "H", "y")
        assert hash(card1) != hash(card2)

    def test_colorcard_is_same_color(self):
        """Test is_same_color method."""
        card1 = ColorCard(10, "H", "g")
        card2 = ColorCard(14, "D", "g")
        card3 = ColorCard(10, "H", "y")

        assert card1.is_same_color(card2) is True
        assert card1.is_same_color(card3) is False

    def test_colorcard_pstr_has_colored_background(self):
        """Test ColorCard pstr has color-coded background."""
        green = ColorCard(10, "H", "g")
        yellow = ColorCard(10, "H", "y")
        grey = ColorCard(10, "H", "e")

        # All should contain ANSI codes
        assert "\033[" in green.pstr()
        assert "\033[" in yellow.pstr()
        assert "\033[" in grey.pstr()

        # Different colors should produce different output
        assert green.pstr() != yellow.pstr()
        assert yellow.pstr() != grey.pstr()

    def test_colorcard_inherits_from_card(self):
        """Test that ColorCard is a subclass of Card."""
        card = ColorCard(10, "H", "g")
        assert isinstance(card, Card)

    def test_colorcard_comparison_operators(self):
        """Test ColorCard inherits comparison from Card (ignores color)."""
        card1 = ColorCard(9, "H", "g")
        card2 = ColorCard(10, "H", "y")
        assert card1 < card2  # Comparison based on rank only


class TestCardEdgeCases:
    """Test edge cases and special scenarios."""

    def test_card_comparison_with_non_card(self):
        """Test that comparing Card with non-Card returns NotImplemented."""
        card = Card(10, "H")
        result = card.__eq__(42)  # type: ignore[arg-type]
        assert result is NotImplemented

    def test_is_same_suit_with_non_card(self):
        """Test is_same_suit with non-Card returns NotImplemented."""
        card = Card(10, "H")
        result = card.is_same_suit(42)  # type: ignore[arg-type]
        assert result is NotImplemented

    def test_is_same_rank_with_non_card(self):
        """Test is_same_rank with non-Card returns NotImplemented."""
        card = Card(10, "H")
        result = card.is_same_rank(42)  # type: ignore[arg-type]
        assert result is NotImplemented

    def test_multiple_cards_same_values(self):
        """Test creating multiple cards with same values maintains independence."""
        cards = [Card(10, "H") for _ in range(5)]
        assert len(set(id(c) for c in cards)) == 5  # All different objects
        assert len(set(cards)) == 1  # But all equal

    def test_card_index_cache_population(self):
        """Test that card_index_cache gets populated correctly."""
        # Clear any existing cache state by creating new cards
        card1 = Card(7, "S")
        card2 = Card(7, "S")

        # Both should have the same cached index
        assert card1.card_index == card2.card_index

        # Check it's in the cache
        cache_key = (7, "S")
        assert cache_key in Card._card_index_cache
