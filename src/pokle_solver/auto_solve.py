# Support both direct execution and module import
if __name__ == "__main__":
    # Running as script - use absolute imports with sys.path manipulation
    import sys
    from pathlib import Path
    
    # Add parent directory to path so we can import pokle_solver
    src_path = Path(__file__).parent.parent
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    from pokle_solver.card import Card
    from pokle_solver.solver import Solver
else:
    # Running as module - use relative imports
    from .card import Card
    from .solver import Solver
from playwright.sync_api import sync_playwright
import re


if __name__ == "__main__":
    with sync_playwright() as p:
        # Launch the browser and open a new page
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://poklegame.com/")

        # Handle the introduction to the game
        page.locator("#intro-end-button").click()
        page.locator("#tut-more-button-1").click()
        page.locator("#tut-more-button-2").click()
        page.locator("#tut-end-button").click()

        # Extract hole cards for all players
        all_hole_cards = []
        for player in range(1, 4):
            player_hole_cards = []
            for card in range(1, 3):
                rank = page.locator(f"#p{player}card{card}").text_content()
                style = page.locator(f"#p{player}card{card}").get_attribute("style")
                suit_match = re.search(r'url\("(.).+?\.svg', style) if style else None
                suit = suit_match.group(1).upper() if suit_match else None
                player_hole_cards.append(Card.from_string(f"{rank}{suit}"))
            all_hole_cards.append(player_hole_cards)

        # Extract trophy placements for each round
        rounds = ["Flop", "Turn", "River"]
        places = []
        for round_name in rounds:
            row = page.locator(f"tr:has(td.stage-tag:has-text('{round_name}'))")
            trophy_pics = row.locator(".trophy-pic").all()
            round_trophies = []
            for trophy in trophy_pics:
                style = trophy.get_attribute("style")
                trophy_match = re.search(r'url\("([^.]+)\.svg', style) if style else None
                if trophy_match:
                    trophy_str = trophy_match.group(1)
                    round_trophies.append(trophy_str)
            places.append(round_trophies)

        # Convert trophy names to player positions for each round
        place_dict = {"gold": 1, "silver": 2, "bronze": 3}
        for round in range(len(places)):
            places[round] = [i for i, t in sorted(
                enumerate(places[round], start=1), key=lambda it: place_dict[it[1]]
            )]


        solver = Solver(
            all_hole_cards[0], all_hole_cards[1], all_hole_cards[2],
            places[0], places[1], places[2],
        )
        possible_tables = solver.solve()
        print(f"Possible tables found: {len(possible_tables)}")
        solver.print_game(solver.get_maxh_table())
        
        input("Press Enter to close the browser...")
        browser.close()