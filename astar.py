from puzzle import *
import heapq

def astar(state:list , heuristic):

    if not is_solvable(state):
            return None, 0, 0, 0

    heap = []
    visited = set()
    counter = 0
    expanded_counter = 0
    f = heuristic(state)
    heapq.heappush(heap , (f , counter , 0 , state , None , None))

    dirs = ["Up" , "Down" , "Left" , "Right"]
    parent = {}

    while(heap):
        _ , _ , g , current_state , parent_state , d = heapq.heappop(heap)
        key = tuple(current_state)
        if key in visited : continue
        parent[key] = (parent_state , d)

        if is_goal(current_state):
             path = reconstruct_path(parent , current_state)
             return path , expanded_counter , len(path) , g
        
        expanded_counter += 1

        visited.add(key)
        g+=1

        for dir in dirs :
            candidate = find_neighbour(current_state , dir)
            if candidate == current_state :
                continue
            counter += 1
            f = g + heuristic(candidate)
            heapq.heappush(heap , (f  , counter , g , candidate , key , dir))

    return None , 0 , 0 , 0
