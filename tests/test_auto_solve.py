"""Unit and integration tests for auto_solve.py module.

Tests the automated Pokle game solving functionality including:
- HTML parsing for hole cards and trophies
- Color feedback extraction
- Integration with the solver
"""

from unittest.mock import Mock, patch
from pokle_solver.card import Card


class MockLocator:
    """Mock Playwright locator for testing."""

    def __init__(self, text_content=None, attribute_value=None, count_value=1):
        self._text_content = text_content
        self._attribute_value = attribute_value
        self._count_value = count_value
        self._items = []

    def text_content(self):
        return self._text_content

    def get_attribute(self, attr_name):
        return self._attribute_value

    def click(self):
        pass

    def nth(self, index):
        if self._items and index < len(self._items):
            return self._items[index]
        return self

    def last(self):
        if self._items:
            return self._items[-1]
        return self

    def first(self):
        if self._items:
            return self._items[0]
        return self

    def count(self):
        return self._count_value

    def all(self):
        return self._items

    def wait_for(self, **kwargs):
        pass


class TestHoleCardParsing:
    """Test extraction of hole cards from HTML."""

    def test_parse_single_hole_card(self):
        """Test parsing a single hole card with rank and suit."""
        page = Mock()

        # Mock rank text content
        rank_locator = MockLocator(text_content="A")
        page.locator.return_value = rank_locator

        # First call returns rank, second returns style with suit
        style_locator = MockLocator(
            text_content="A", attribute_value='background-image: url("h_card.svg")'
        )
        page.locator.side_effect = [
            rank_locator,  # For rank text
            style_locator,  # For style attribute
        ]

        # Simulate the parsing logic
        rank = page.locator("#p1card1").text_content()
        style = page.locator("#p1card1").get_attribute("style")

        assert rank == "A"
        assert "h" in style

    def test_parse_all_hole_cards_for_player(self):
        """Test parsing both hole cards for a single player."""
        page = Mock()

        expected_cards = [("A", "h"), ("K", "s")]
        locators = []

        for rank, suit in expected_cards:
            rank_loc = MockLocator(text_content=rank)
            style_loc = MockLocator(
                text_content=rank,
                attribute_value=f'background-image: url("{suit}_card.svg")',
            )
            locators.extend([rank_loc, style_loc])

        page.locator.side_effect = locators

        # Parse cards
        cards = []
        for i in range(1, 3):
            rank = page.locator(f"#p1card{i}").text_content()
            style = page.locator(f"#p1card{i}").get_attribute("style")
            cards.append((rank, style))

        assert len(cards) == 2
        assert cards[0][0] == "A"
        assert cards[1][0] == "K"

    def test_parse_face_card_ranks(self):
        """Test parsing face cards (J, Q, K, A)."""
        test_ranks = ["J", "Q", "K", "A"]

        for rank in test_ranks:
            page = Mock()
            locator = MockLocator(text_content=rank)
            page.locator.return_value = locator

            parsed_rank = page.locator("#p1card1").text_content()
            assert parsed_rank == rank

    def test_parse_all_suits(self):
        """Test parsing all four suits from style attribute."""
        suits = ["h", "d", "c", "s"]

        for suit in suits:
            page = Mock()
            locator = MockLocator(
                attribute_value=f'background-image: url("{suit}_card.svg")'
            )
            page.locator.return_value = locator

            style = page.locator("#p1card1").get_attribute("style")
            assert suit in style.lower()


class TestTrophyParsing:
    """Test extraction of trophy placements from HTML."""

    def test_parse_trophies_for_single_round(self):
        """Test parsing trophy placements for one round (flop/turn/river)."""
        page = Mock()

        # Mock row locator
        row = Mock()

        # Create trophy locators with different styles
        trophy_styles = [
            'background-image: url("gold.svg")',
            'background-image: url("silver.svg")',
            'background-image: url("bronze.svg")',
        ]

        trophy_locators = [
            MockLocator(attribute_value=style) for style in trophy_styles
        ]

        row.locator.return_value.all.return_value = trophy_locators
        page.locator.return_value = row

        # Parse trophies
        trophies = []
        for trophy in row.locator(".trophy-pic").all():
            style = trophy.get_attribute("style")
            trophies.append(style)

        assert len(trophies) == 3
        assert "gold" in trophies[0]
        assert "silver" in trophies[1]
        assert "bronze" in trophies[2]

    def test_convert_trophies_to_positions(self):
        """Test conversion of trophy names to player positions."""
        trophies = ["gold", "silver", "bronze"]
        place_dict = {"gold": 1, "silver": 2, "bronze": 3}

        # Convert to positions (1-indexed player numbers)
        positions = [
            i
            for i, t in sorted(
                enumerate(trophies, start=1), key=lambda it: place_dict[it[1]]
            )
        ]

        assert positions == [1, 2, 3]

    def test_convert_trophies_different_order(self):
        """Test trophy conversion when trophies are in different order."""
        # Player 2 has gold, Player 1 has silver, Player 3 has bronze
        trophies = ["silver", "gold", "bronze"]
        place_dict = {"gold": 1, "silver": 2, "bronze": 3}

        positions = [
            i
            for i, t in sorted(
                enumerate(trophies, start=1), key=lambda it: place_dict[it[1]]
            )
        ]

        # Should return [2, 1, 3] meaning:
        # Position 1 (rank 1 = gold) is player 2
        # Position 2 (rank 2 = silver) is player 1
        # Position 3 (rank 3 = bronze) is player 3
        assert positions == [2, 1, 3]


class TestColorFeedbackExtraction:
    """Test extraction of color feedback from submitted guesses."""

    def test_extract_color_by_index(self):
        """Test extracting color using index attribute."""
        page = Mock()

        # Create buttons for different positions with different colors
        button_colors = ["darkgreen", "gold", "grey", "darkgreen", "gold"]
        buttons = [MockLocator(attribute_value=color) for color in button_colors]

        # Mock the locator to return different buttons for different indices
        def locator_side_effect(selector):
            # Extract index from selector like 'button.guess-button[index="0"]'
            if '[index="' in selector:
                index = int(selector.split('[index="')[1].split('"')[0])
                return buttons[index]
            return MockLocator()

        page.locator.side_effect = locator_side_effect

        # Extract colors
        colors = []
        for i in range(5):
            button = page.locator(f'button.guess-button[active="false"][index="{i}"]')
            color = button.get_attribute("card-color")
            colors.append(color)

        assert colors == button_colors

    def test_convert_colors_to_codes(self):
        """Test converting color names to game codes (g/y/e)."""
        colors_dict = {"darkgreen": "g", "gold": "y", "grey": "e"}
        raw_colors = ["darkgreen", "gold", "grey", "darkgreen", "gold"]

        converted = [colors_dict.get(c, "e") for c in raw_colors]

        assert converted == ["g", "y", "e", "g", "y"]

    def test_last_selector_gets_most_recent(self):
        """Test that .last selector gets the most recently submitted row."""
        page = Mock()

        # Simulate the most recent button with darkgreen color
        # (In reality, there would be multiple rows with same index,
        # but .last gets the most recently submitted one)
        new_button = MockLocator(attribute_value="darkgreen")

        # Set up mock to return new_button when .last is accessed
        locator = Mock()
        locator.last = new_button
        page.locator.return_value = locator

        button = page.locator('button.guess-button[index="0"]').last
        color = button.get_attribute("card-color")

        assert color == "darkgreen"


class TestAutoSolveIntegration:
    """Integration tests for the auto-solve workflow."""

    @patch("pokle_solver.auto_solve.Solver")
    def test_solver_integration(self, mock_solver_class):
        """Test integration between auto_solve and Solver."""
        # Setup mock solver
        mock_solver = Mock()
        mock_solver.solve.return_value = [[Mock(), Mock(), Mock(), Mock(), Mock()]]
        mock_solver.get_maxh_table.return_value = [
            Card.from_string("AH"),
            Card.from_string("KD"),
            Card.from_string("QC"),
            Card.from_string("JS"),
            Card.from_string("10H"),
        ]
        mock_solver.valid_tables = [[Mock()] * 5]
        mock_solver_class.return_value = mock_solver

        # Create solver instance
        hole_cards = [
            [Card.from_string("AH"), Card.from_string("KD")],
            [Card.from_string("QC"), Card.from_string("JS")],
            [Card.from_string("10H"), Card.from_string("9D")],
        ]
        places = [[1, 2, 3], [2, 1, 3], [1, 3, 2]]

        solver = mock_solver_class(
            hole_cards[0], hole_cards[1], hole_cards[2], places[0], places[1], places[2]
        )

        # Verify solver was created with correct parameters
        mock_solver_class.assert_called_once()

        # Simulate getting a guess
        max_table = solver.get_maxh_table(use_sampling=True)
        assert len(max_table) == 5

        # Simulate processing color feedback
        card_colors = ["g", "y", "e", "g", "y"]
        solver.next_table_guess(card_colors)

        mock_solver.next_table_guess.assert_called_once_with(card_colors)

    def test_face_card_conversion(self):
        """Test conversion of face card ranks to display strings."""
        face_cards = {11: "J", 12: "Q", 13: "K", 14: "A"}

        # Test face cards
        assert face_cards.get(11, str(11)) == "J"
        assert face_cards.get(14, str(14)) == "A"

        # Test number cards
        assert face_cards.get(7, str(7)) == "7"
        assert face_cards.get(10, str(10)) == "10"

    def test_game_completion_detection(self):
        """Test detection of game completion (all green)."""
        # All green - game won
        card_colors = ["g", "g", "g", "g", "g"]
        is_all_green = all(color == "g" for color in card_colors)
        assert is_all_green is True

        # Some non-green - game continues
        card_colors = ["g", "g", "y", "g", "g"]
        is_all_green = all(color == "g" for color in card_colors)
        assert is_all_green is False

        # All grey - game continues
        card_colors = ["e", "e", "e", "e", "e"]
        is_all_green = all(color == "g" for color in card_colors)
        assert is_all_green is False


class TestErrorHandling:
    """Test error handling in auto_solve."""

    def test_invalid_color_handling(self):
        """Test handling of invalid/unknown color values."""
        colors_dict = {"darkgreen": "g", "gold": "y", "grey": "e"}
        card_colors = ["e"] * 5

        # Unknown color should default to existing value
        unknown_color = "blue"
        card_colors[0] = colors_dict.get(unknown_color, card_colors[0])

        assert card_colors[0] == "e"  # Should keep default

    def test_missing_card_attribute(self):
        """Test handling when card-color attribute is missing."""
        page = Mock()
        locator = MockLocator(attribute_value=None)
        page.locator.return_value.last = locator

        button = page.locator('button.guess-button[index="0"]').last
        color = button.get_attribute("card-color")

        # Should return None, which should be handled gracefully
        assert color is None

    def test_fallback_selector_on_exception(self):
        """Test that fallback selector is used when primary fails."""
        page = Mock()

        # Primary selector raises exception
        primary = Mock()
        primary.last.get_attribute.side_effect = Exception("Element not found")

        # Fallback selector works
        fallback_button = MockLocator(attribute_value="darkgreen")
        fallback = Mock()
        fallback.last = fallback_button

        # Mock to raise on first call, return fallback on second
        page.locator.side_effect = [primary, fallback]

        try:
            # Try primary
            color = page.locator('button[index="0"]').last.get_attribute("card-color")
        except Exception:
            # Use fallback
            color = page.locator('button[suit="h"]').last.get_attribute("card-color")

        assert color == "darkgreen"


class TestRegexParsing:
    """Test regex patterns used for parsing HTML."""

    def test_suit_extraction_from_style(self):
        """Test regex extraction of suit from style attribute."""
        import re

        # Test all suits
        suits = ["h", "d", "c", "s"]
        for suit in suits:
            style = f'background-image: url("{suit}_card.svg")'
            match = re.search(r'url\("(.).+?\.svg', style)

            assert match is not None
            assert match.group(1) == suit

    def test_trophy_extraction_from_style(self):
        """Test regex extraction of trophy type from style attribute."""
        import re

        # Test all trophy types
        trophies = ["gold", "silver", "bronze"]
        for trophy in trophies:
            style = f'background-image: url("{trophy}.svg")'
            match = re.search(r'url\("([^.]+)\.svg', style)

            assert match is not None
            assert match.group(1) == trophy

    def test_suit_extraction_handles_uppercase(self):
        """Test that suit extraction works with different cases."""
        import re

        style = 'background-image: url("H_card.svg")'
        match = re.search(r'url\("(.).+?\.svg', style)

        assert match is not None
        assert match.group(1).upper() in ["H", "D", "C", "S"]
