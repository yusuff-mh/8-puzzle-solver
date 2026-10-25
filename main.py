import argparse
import random
import time
from puzzle import find_neighbour, is_solvable
from Uniformed_Search import bfs, dfs, ids
from astar import astar
from heuristics import manhattan, euclidean
 
GOAL = [0, 1, 2, 3, 4, 5, 6, 7, 8]
 

ALGORITHMS = [
    ("BFS", bfs, ()),
    ("DFS", dfs, ()),
    ("IDS", ids, ()),
    ("A* Manhattan", astar, (manhattan,)),
    ("A* Euclidean", astar, (euclidean,)),
]
 

def parse_state(text):
   
    parts = text.replace(",", " ").split()
    try:
        state = [int(p) for p in parts]
    except ValueError:
        raise ValueError("State must contain only numbers.")
    if sorted(state) != GOAL:
        raise ValueError("State must contain each number from 0 to 8 exactly once.")
    return state
 
 
def random_state():
    
    while True:
        state = random.sample(GOAL, 9)
        if is_solvable(state):
            return state
 
 
def run_algorithm(name, func, state, *extra):
   
    start = time.perf_counter()
    result = func(list(state), *extra)
    elapsed = time.perf_counter() - start
 
    path, expanded, cost, depth = result
    return {
        "name": name,
        "path": path,          
        "expanded": expanded, 
        "cost": cost,          
        "depth": depth,        
        "time": elapsed,      
    }
 
 
def replay(state, path):
   
    boards = [list(state)]
    for move in path:
        boards.append(find_neighbour(boards[-1], move))
    return boards
 
 

def board_lines(board):
    
    cells = [str(x) if x != 0 else "_" for x in board]
    return [" ".join(cells[r * 3:(r + 1) * 3]) for r in range(3)]
 
 
def print_board(board, title=None):
    if title:
        print(title)
    print("+---+---+---+")
    for r in range(3):
        row = board[r * 3:(r + 1) * 3]
        print("| " + " | ".join(str(x) if x != 0 else " " for x in row) + " |")
        print("+---+---+---+")
 
 
def print_steps(state, path, per_row=5):
    
    boards = replay(state, path)
    width = 16
    for start in range(0, len(boards), per_row):
        chunk = range(start, min(start + per_row, len(boards)))
        titles = []
        for i in chunk:
            titles.append(("Start" if i == 0 else f"{i}: {path[i - 1]}").ljust(width))
        print("".join(titles))
        for line in range(3):
            print("".join(board_lines(boards[i])[line].ljust(width) for i in chunk))
        print()
 
 
def print_result(res):
    print("=" * 50)
    print(res["name"])
    if res["path"] is None:
        print("No solution found")
        return
    print(f"  Cost of path   : {res['cost']}")
    print(f"  Nodes expanded : {res['expanded']}")
    print(f"  Search depth   : {res['depth']}")
    print(f"  Running time   : {res['time']:.4f} s")
    if len(res["path"]) <= 40:
        print("  Path           :", ", ".join(res["path"]) or "(already at goal)")
    else:
        print(f"  Path           : {len(res['path'])} moves (too long to print)")
 
 
def print_summary(results):
    print()
    print("=" * 50)
    print("SUMMARY")
    header = f"{'Algorithm':<15}{'Cost':>8}{'Expanded':>12}{'Depth':>8}{'Time (s)':>12}"
    print(header)
    print("-" * len(header))
    for r in results:
        if r["path"] is None:
            print(f"{r['name']:<15}{'-':>8}{'-':>12}{'-':>8}{r['time']:>12.4f}")
        else:
            print(f"{r['name']:<15}{r['cost']:>8}{r['expanded']:>12}"
                  f"{r['depth']:>8}{r['time']:>12.4f}")
    print("Depth note: BFS/A* = depth of the solution, DFS = deepest level "
          "reached, IDS = final depth limit.")
 

def get_initial_state(args):
    if args.state:
        return parse_state(args.state)
    if args.random:
        return random_state()
    text = input("Enter 9 numbers (e.g. 1,2,5,3,4,0,6,7,8), "
                 "'r' for random, or Enter for the PDF example: ").strip()
    if text == "":
        return [1, 2, 5, 3, 4, 0, 6, 7, 8]
    if text.lower() == "r":
        return random_state()
    return parse_state(text)
 
 
def main():
    parser = argparse.ArgumentParser(description="8-puzzle search algorithms")
    parser.add_argument("--state", help="initial state, e.g. 1,2,5,3,4,0,6,7,8")
    parser.add_argument("--random", action="store_true", help="random solvable state")
    parser.add_argument("--steps", action="store_true",
                        help="print the board after every move of the A* Manhattan solution")
    parser.add_argument("--skip", nargs="*", default=[],
                        help="algorithms to skip, e.g. --skip DFS IDS")
    args = parser.parse_args()
 
    try:
        state = get_initial_state(args)
    except ValueError as e:
        print("Invalid state:", e)
        return
 
    print_board(state, "Initial state:")
    if not is_solvable(state):
        print("This state has no solution (odd number of inversions).")
        return
 
    skip = {s.lower() for s in args.skip}
    results = []
    for name, func, extra in ALGORITHMS:
        if name.lower() in skip or name.split()[0].lower() in skip:
            continue
        print(f"Running {name} ...", flush=True)
        res = run_algorithm(name, func, state, *extra)
        results.append(res)
        print_result(res)
 
    print_summary(results)
 
    if args.steps:
        best = next((r for r in results if r["name"] == "A* Manhattan"), None) \
            or next((r for r in results if r["path"] is not None), None)
        if best:
            print(f"\nStep by step ({best['name']}):\n")
            print_steps(state, best["path"])
 
 
if __name__ == "__main__":
    main()