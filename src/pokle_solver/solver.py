from card import Card
from itertools import combinations
import pandas as pd
from scipy.stats import entropy
from table import Table, HandRanking
from dataclasses import dataclass

@dataclass
class PhaseEvaluation:
    """Configuration for evaluating a poker phase (flop, turn, or river)."""
    table: Table
    expected_rankings: list
    prev_cards_used: set = None
    validate_all_cards_used: bool = False

MASTER_DECK = [
    Card(rank, suit) for rank in range(2, 15) for suit in ["H", "D", "C", "S"]
]


class Solver:
    def __init__(
        self,
        p1hole: list,
        p2hole: list,
        p3hole: list,
        flop_hand_ranks: list,
        turn_hand_ranks: list,
        river_hand_ranks: list,
    ):
        # Validate hole cards
        for p_name, p_hole in zip(["P1", "P2", "P3"], [p1hole, p2hole, p3hole]):
            if (
                not isinstance(p_hole, list)
                or len(p_hole) != 2
                or not all(isinstance(card, Card) for card in p_hole)
            ):
                raise ValueError(
                    f"{p_name} hole cards must be a list of exactly 2 Card objects."
                )

        # Updated validation for hand ranks
        for hand_rank_lists in [flop_hand_ranks, turn_hand_ranks, river_hand_ranks]:
            if not isinstance(hand_rank_lists, list) or sorted(hand_rank_lists) != [1, 2, 3]:
                raise ValueError(
                    "Hand rank lists must be a permutation of [1, 2, 3]"
                )

        self.hole_cards = {"P1": p1hole, "P2": p2hole, "P3": p3hole}

        self.flop_hand_ranks = flop_hand_ranks
        self.turn_hand_ranks = turn_hand_ranks
        self.river_hand_ranks = river_hand_ranks

        self.current_deck = MASTER_DECK.copy()
        self.__valid_rivers = []
        self.__river_entropies = pd.Series()
        self.__table_comparisons = pd.DataFrame()
        self.__comparisons_matrix = pd.DataFrame()
        self.__maxh_table = tuple()
        self.__used_tables = []

    @property
    def valid_rivers(self):
        """Get the list of valid river tables."""
        return self.__valid_rivers

    def __possible_flops(self):
        """Find all possible flops that maintain the current player rankings.

        Returns:
            list: A list of tuples (table, cards_used_in_hands) where cards_used_in_hands 
                  is a set of board cards used in any player's best hand at the flop.
        """
        hole_cards = {card for hole in self.hole_cards.values() for card in hole}
        remaining_cards = set(self.current_deck).difference(hole_cards)
        self.current_deck = list(remaining_cards)
        
        all_flops = list(combinations(self.current_deck, 3))

        valid_flops = []
        for flop in all_flops:
            flop_table = Table(flop)
            
            phase_eval = PhaseEvaluation(
                table=flop_table,
                expected_rankings=self.flop_hand_ranks
            )
            is_valid, cards_used = self.__evaluate_phase(phase_eval)
            
            if is_valid:
                valid_flops.append((flop_table, cards_used))

        return valid_flops

    def __evaluate_phase(self, phase_eval: PhaseEvaluation):
        """Helper method to evaluate hands for all players at a given phase.

        Args:
            phase_eval (PhaseEvaluation): Configuration object containing table, rankings, 
                                           and validation parameters.

        Returns:
            tuple: (is_valid, cards_used_accumulated) where is_valid indicates if this table 
                   matches expected rankings, and cards_used_accumulated is the set of all 
                   cards used across phases.
        """
        all_hole_cards = {card for hole in self.hole_cards.values() for card in hole}
        current_player_ranks = []
        cards_used_current_phase = set()
        
        for player, hole in self.hole_cards.items():
            # adds the player name, hand rank, tie breaker list, and best hand
            player_hand = phase_eval.table.rank_hand(hole)
            current_player_ranks.append((player, player_hand.rank, player_hand.tie_breakers, player_hand.best_hand))
            
            # Collect cards used in current phase (exclude flush hands)
            if player_hand.rank != 6:  # Not a flush
                cards_used_current_phase.update(set(player_hand.best_hand))

        # Accumulate cards used across all phases
        if phase_eval.prev_cards_used is not None:
            cards_used_accumulated = phase_eval.prev_cards_used | cards_used_current_phase
        else:
            cards_used_accumulated = cards_used_current_phase
        
        cards_used_accumulated.difference_update(all_hole_cards)
        
        # For river, validate that all board cards were used at some point
        if phase_eval.validate_all_cards_used and cards_used_accumulated != set(phase_eval.table.cards):
            return False, cards_used_accumulated

        # Check for ties in hand rankings
        hand_comparators = {(player[1], player[2]) for player in current_player_ranks}
        if len(hand_comparators) < 3:
            return False, cards_used_accumulated

        # Sort by rank and tie breakers
        current_player_ranks.sort(reverse=True, key=lambda x: (x[1], x[2]))
        
        # Map player names to their rankings (1=best, 2=second, 3=third)
        current_player_ranks_comparable = [
            int(player[0][1]) for player in current_player_ranks
        ]
        
        is_valid = current_player_ranks_comparable == phase_eval.expected_rankings
        return is_valid, cards_used_accumulated

    def __find_valid_next_phase(
        self, 
        prev_phase_results: list, 
        expected_rankings: list, 
        validate_all_cards_used: bool = False
    ):
        """Helper method to find valid tables for the next phase (turn or river).

        Args:
            prev_phase_results (list): List of tuples (table, cards_used) from previous phase.
            expected_rankings (list): Expected hand rankings for this phase.
            validate_all_cards_used (bool): Whether to validate all cards were used.

        Returns:
            list: List of tuples (table, cards_used_accumulated) for valid combinations.
        """
        valid_tables = []
        
        for prev_table, prev_cards_used in prev_phase_results:
            remaining_deck = set(self.current_deck) - set(prev_table.cards)

            for next_card in remaining_deck:
                next_table = prev_table.add_cards(next_card)
                
                phase_eval = PhaseEvaluation(
                    table=next_table,
                    expected_rankings=expected_rankings,
                    prev_cards_used=prev_cards_used,
                    validate_all_cards_used=validate_all_cards_used
                )
                is_valid, cards_used = self.__evaluate_phase(phase_eval)
                
                if is_valid:
                    valid_tables.append((next_table, cards_used))

        return valid_tables

    def __possible_turns(self, flops: list):
        """Find all possible turns that maintain the current player rankings.

        Args:
            flops (list): A list of tuples (table, cards_used) from flop phase.

        Returns:
            list: A list of tuples (table, cards_used_accumulated) for valid turn combinations.
        """
        return self.__find_valid_next_phase(flops, self.turn_hand_ranks)

    def __possible_rivers(self, turns: list):
        """Find all possible rivers that maintain the current player rankings.

        Args:
            turns (list): A list of tuples (table, cards_used) from turn phase.

        Returns:
            list: A list of tuples (table, cards_used_accumulated) for valid river combinations.
        """
        return self.__find_valid_next_phase(
            turns, 
            self.river_hand_ranks, 
            validate_all_cards_used=True
        )

    def __entropy_from_series(self, s: pd.Series):
        """Calculates the Shannon entropy from a pandas series.

        Args:
            s (pd.Series): A pandas series. Each value in the series represents a category.

        Returns:
            float: The Shannon entropy of the series.
        """
        return entropy(s.value_counts(normalize=True), base=2)

    def get_maxh_table(self):
        """Returns a pandas series for each possible river with it's respective Shannon entropy value ordered from highest to lowest.

        Returns:
            tuple: A tuple of 5 Card objects representing the river with the highest entropy.
        """
        # Validate state
        if not getattr(self, "_Solver__valid_rivers", None):
            raise ValueError("No possible rivers calculated. Please run solve() first.")

        rivers = pd.Series(self.__valid_rivers)
        temp_df = pd.DataFrame({"rivers": rivers, "key": 1})
        self.__table_comparisons = temp_df.merge(
            temp_df, on="key", suffixes=("_guess", "_answer")
        ).drop("key", axis=1)
        self.__table_comparisons.rename(
            columns={"rivers_guess": "guess", "rivers_answer": "answer"}, inplace=True
        )
        self.__table_comparisons["table_comparison"] = self.__table_comparisons.apply(
            lambda row: row["guess"].compare(row["answer"]), axis=1
        )
        self.__table_comparisons[["guess_str", "answer_str"]] = self.__table_comparisons[
            ["guess", "answer"]
        ].astype(str)
        self.__comparisons_matrix = self.__table_comparisons.pivot(
            index="answer_str", columns="guess_str", values="table_comparison"
        )

        self.__river_entropies = self.__comparisons_matrix.apply(
            self.__entropy_from_series, axis=0
        ).sort_values(ascending=False)

        maxh_table_str = self.__river_entropies.index[0]
        self.__maxh_table = self.__table_comparisons[
            self.__table_comparisons["guess_str"] == maxh_table_str
        ]["guess"].iloc[0]

        return self.__maxh_table

    def next_table_guess(self, table_colors: list, current_guess: Table = None):
        """Given a current guess and the resulting table colors, filter the possible rivers to those that match the colors.

        Args:
            current_guess (Table): A Table object representing the current guess.
            table_colors (list): A list of three strings representing the colors of all five cards in the guess. _g = green, _y = yellow, <empty string> = grey.
            e.g. ['_g', '_y', '', '_g', '']

        Returns:
            list: A filtered list of possible rivers that match the given colors.
        """
        if current_guess is None:
            current_guess = self.__maxh_table
        if not getattr(self, "_Solver__valid_rivers", None):
            raise ValueError("No possible rivers calculated. Please run solve() first.")
        if not isinstance(current_guess, Table) or not current_guess.flop or not current_guess.turn or not current_guess.river:
            raise ValueError("Current guess must be a complete Table object with flop, turn, and river.")
        if not isinstance(table_colors, list) or len(table_colors) != 5:
            raise ValueError(
                "Table colors must be a list of 5 colors for each card in the table."
            )
        
        possible_outcomes = self.__comparisons_matrix[str(current_guess)]

        color_current_guess = current_guess.update_colors(table_colors)
        self.__used_tables.append(color_current_guess)

        possible_outcomes_filtered = possible_outcomes[
            possible_outcomes == color_current_guess
        ].index
        if possible_outcomes_filtered.empty:
            raise ValueError(
                "No possible rivers match the given colors for the current guess."
            )
        comparisons_filtered = self.__table_comparisons[
            self.__table_comparisons["guess_str"].isin(possible_outcomes_filtered)
        ]
        comparisons_filtered = comparisons_filtered[['guess_str', 'guess']].drop_duplicates(subset=['guess_str'])
        self.__valid_rivers = comparisons_filtered['guess'].tolist()

        return self.__valid_rivers

    def solve(self):
        """Find all possible board runouts that maintain the current player rankings.

        Returns:
            list: A list of valid Table objects representing complete board runouts.
        """
        flops = self.__possible_flops()
        turns = self.__possible_turns(flops)
        river_results = self.__possible_rivers(turns)
        
        # Extract just the tables (drop the cards_used metadata)
        self.__valid_rivers = [table for table, _ in river_results]

        return self.__valid_rivers

    @staticmethod
    def __player_hand_place(hand_ranks: list):
        """Convert list of player hands ordered by hand strength to a list of places for each player.

        Args:
            hand_ranks (list): A list of player hand ranks ordered by hand strength.

        Returns:
            list: A list where the index represents the player (0=P1, 1=P2, 2=P3) and the value represents their place (1=best, 2=second, 3=third).

        Example:
            >>> hand_ranks = [3, 1, 2]  # P2 has best hand, P1 second, P3 third
            >>> Solver.__player_hand_place(hand_ranks)
            [2, 3, 1]
        """
        enum_rankings = [(index, player) for index, player in enumerate(hand_ranks, start=1)]
        enum_rankings.sort(key=lambda x: x[1])  # Sort by player number
        return [place for place, _ in enum_rankings]

    def print_game(self, table: Table, is_win: bool = False):
        """Prints the game state for a given table."""
        if not self.__valid_rivers:
            raise ValueError("No possible rivers calculated. Please run solve() first.")
        if not isinstance(table, Table):
            raise ValueError("Table must be an instance of the Table class.")
        if table not in self.__valid_rivers:
            raise ValueError("Provided table is not in the list of possible rivers.")

        hand_rank_symbols = {
            1: "HC",
            2: "1P",
            3: "2P",
            4: "3K",
            5: "St",
            6: "Fl",
            7: "FH",
            8: "4K",
            9: "SF",
        }
        
        # Format hole cards
        p1_0 = self.hole_cards["P1"][0].pstr().ljust(3)
        p2_0 = self.hole_cards["P2"][0].pstr().ljust(3)
        p3_0 = self.hole_cards["P3"][0].pstr().ljust(3)
        p1_1 = self.hole_cards["P1"][1].pstr().ljust(3)
        p2_1 = self.hole_cards["P2"][1].pstr().ljust(3)
        p3_1 = self.hole_cards["P3"][1].pstr().ljust(3)

        # Calculate hand ranks for flop
        flop_table = Table(*list(table.flop))
        p1_flop = hand_rank_symbols[flop_table.rank_hand(self.hole_cards["P1"]).rank] + "\033[0m"
        p2_flop = hand_rank_symbols[flop_table.rank_hand(self.hole_cards["P2"]).rank] + "\033[0m"
        p3_flop = hand_rank_symbols[flop_table.rank_hand(self.hole_cards["P3"]).rank] + "\033[0m"
        
        # Calculate hand ranks for turn
        turn_table = Table(*list(table.flop), table.turn)
        p1_turn = hand_rank_symbols[turn_table.rank_hand(self.hole_cards["P1"]).rank] + "\033[0m"
        p2_turn = hand_rank_symbols[turn_table.rank_hand(self.hole_cards["P2"]).rank] + "\033[0m"
        p3_turn = hand_rank_symbols[turn_table.rank_hand(self.hole_cards["P3"]).rank] + "\033[0m"
        
        # Calculate hand ranks for river (full table)
        p1_river = hand_rank_symbols[table.rank_hand(self.hole_cards["P1"]).rank] + "\033[0m"
        p2_river = hand_rank_symbols[table.rank_hand(self.hole_cards["P2"]).rank] + "\033[0m"
        p3_river = hand_rank_symbols[table.rank_hand(self.hole_cards["P3"]).rank] + "\033[0m"

        # Format table cards for display

        flop_places = self.__player_hand_place(self.flop_hand_ranks)
        turn_places = self.__player_hand_place(self.turn_hand_ranks)
        river_places = self.__player_hand_place(self.river_hand_ranks)
        bg_colors = {1: "\033[48;2;255;215;0m", 2: "\033[48;2;192;192;192m", 3: "\033[48;2;205;127;50m"}

        print("Pokle Solver Results")
        print("              P1   P2   P3")
        print("             ---  ---  ---")
        print(f"             {p1_0}  {p2_0}  {p3_0}")
        print(f"             {p1_1}  {p2_1}  {p3_1}")
        print("      ------ ---  ---  ---")
        print(f"       flop:  {bg_colors[flop_places[0]]}{p1_flop}   {bg_colors[flop_places[1]]}{p2_flop}   {bg_colors[flop_places[2]]}{p3_flop}")
        print(f"       turn:  {bg_colors[turn_places[0]]}{p1_turn}   {bg_colors[turn_places[1]]}{p2_turn}   {bg_colors[turn_places[2]]}{p3_turn}")
        print(f"      river:  {bg_colors[river_places[0]]}{p1_river}   {bg_colors[river_places[1]]}{p2_river}   {bg_colors[river_places[2]]}{p3_river}")
        print("|-----flop----|-turn|river|")
        for t in self.__used_tables:
            c_flop_cards = [card.pstr().ljust(3) for card in t.cards[:3]]
            c_turn_card = t.turn.pstr().ljust(3)
            c_river_card = t.river.pstr().ljust(3)
            print(f"| {c_flop_cards[0]} {c_flop_cards[1]} {c_flop_cards[2]} | {c_turn_card} | {c_river_card} |")
        if not is_win:
            flop_cards = [card.pstr().ljust(3) for card in table.cards[:3]]
            turn_card = table.turn.pstr().ljust(3)
            river_card = table.river.pstr().ljust(3)
            print(f"| {flop_cards[0]} {flop_cards[1]} {flop_cards[2]} | {turn_card} | {river_card} |")
        print()