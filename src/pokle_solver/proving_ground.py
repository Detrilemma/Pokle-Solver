import os
# ARM64 LLVM optimization workaround
# Use generic ARM64 target to avoid CPU-specific scheduling model bugs
os.environ['NUMBA_CPU_NAME'] = 'generic'
from card import Card, ColorCard
from solver import Solver
from table import Table
import pandas as pd
from scipy.stats import entropy
import polars as pl
import numpy as np

from numba import guvectorize, int64

@guvectorize([(int64[:], int64, int64[:])], '(n),()->(n)', nopython=True)
def g(x, y, res):
    for i in range(x.shape[0]):
        res[i] = x[i] + y

def entropy_from_series(s: pd.Series):
    """Calculates the Shannon entropy from a pandas series.

    Args:
        s (pd.Series): A pandas series. Each value in the series represents a category.

    Returns:
        float: The Shannon entropy of the series.
    """
    return entropy(s.value_counts(normalize=True), base=2)

def pd_method(rivers):
    rivers_str = [str(river) for river in rivers]
    rivers_df = pd.DataFrame({"str_rivers": rivers_str, "rivers": rivers})
    rivers_merged = rivers_df.merge(rivers_df, how="cross", suffixes=("_guess", "_answer"))
    rivers_zipped = zip(rivers_merged["rivers_guess"], rivers_merged["rivers_answer"])
    rivers_merged["compare_result"] = [
        guess.compare(answer) for guess, answer in rivers_zipped
    ]
    entropies = rivers_merged.groupby("str_rivers_guess")["compare_result"].apply(entropy_from_series)
    maxh_table_str = entropies.idxmax()
    maxh_table = rivers_df[rivers_df["str_rivers"] == maxh_table_str]["rivers"].values[0]

    return maxh_table

def pd_method_batch(rivers):
    rivers_str = [str(river) for river in rivers]
    rivers_df = pd.DataFrame({"str_rivers": rivers_str, "rivers": rivers})
    rivers_merged = rivers_df.merge(rivers_df, how="cross", suffixes=("_guess", "_answer"))
    rivers_zipped = zip(rivers_merged["rivers_guess"], rivers_merged["rivers_answer"])
    rivers_merged["compare_result"] = [
        guess.compare(answer) for guess, answer in rivers_zipped
    ]
    rivers_merged["compare_result_str"] = rivers_merged["compare_result"].astype(str)
    entropies_s = pd.Series(dtype=float)
    iterations = 0
    for river_str in rivers_str:
        entropies_s[river_str] = entropy_from_series(
            rivers_merged[rivers_merged["str_rivers_guess"] == river_str]["compare_result_str"]
        )
        iterations += 1
        print(f"Processed {iterations}/{len(rivers_str)} rivers", end="\r")
    return entropies_s

def pl_method(rivers):
    rivers_str = [str(river) for river in rivers]
    rivers_dict = dict(zip(rivers_str, rivers))  # For lookups if needed
    rivers_lf = pl.DataFrame({"rivers_str_guess": rivers_str}).lazy()
    # Now work with strings only in Polars
    rivers_merged = rivers_lf.join(rivers_lf, how="cross", suffix="_answer")
    rivers_zipped = zip(rivers_merged["rivers_guess"], rivers_merged["rivers_answer"])
    rivers_merged["compare_result"] = [
        guess.compare(answer) for guess, answer in rivers_zipped
    ]
    entropies = rivers_merged.groupby("str_rivers_guess")["compare_result"].apply(entropy_from_series)
    maxh_table_str = entropies.idxmax()
    maxh_table = rivers_dict[maxh_table_str]

    return maxh_table

if __name__ == "__main__":
    #  super slow output for testing
    # p1_hole = [Card.from_string("JH"), Card.from_string("6H")]
    # p2_hole = [Card.from_string("4H"), Card.from_string("7S")]
    # p3_hole = [Card.from_string("5D"), Card.from_string("8D")]

    # flop = [3, 2, 1]
    # turn = [2, 3, 1]
    # river = [2, 1, 3]

    # slow output for testing
    p1_hole = [Card.from_string("KH"), Card.from_string("6S")]
    p2_hole = [Card.from_string("8C"), Card.from_string("8H")]
    p3_hole = [Card.from_string("4H"), Card.from_string("9S")]

    flop = [2, 3, 1]
    turn = [3, 2, 1]
    river = [3, 1, 2]

    solver = Solver(p1_hole, p2_hole, p3_hole, flop, turn, river)
    rivers = solver.solve()
    print(f"Possible rivers found: {len(rivers)}")
    # rivers_df = pd.DataFrame([str(river) for river in possible_rivers], columns=['river'])
    # rivers_df.to_csv('river1323.csv', index=False)

    # csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'river1323.csv')
    # rivers_str = pd.read_csv(csv_path)['river'].tolist()
    # rivers = [[Card.from_string(card) for card in river.split()] for river in rivers_str]
    # rivers = [Table(river) for river in rivers]

    rivers_df = pd.DataFrame({'flop': [table.cards[:3] for table in rivers]})
    
    # Check for flops with same cards but different order
    # Convert each flop to a frozenset (order-independent) for comparison
    rivers_df['flop_set'] = rivers_df['flop'].apply(lambda x: frozenset(x))
    
    # Count unique flops by content (ignoring order)
    print(rivers_df['flop_set'].nunique())
    print(rivers_df["flop"].nunique())