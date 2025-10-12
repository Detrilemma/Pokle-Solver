from card import Card
from solver import Solver

def test_flop_generation():
    solver = Solver()
    flops = solver.possible_flops()
    print(len(flops))

if __name__ == "__main__":
    test_flop_generation()
