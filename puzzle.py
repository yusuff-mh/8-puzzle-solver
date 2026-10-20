def find_neighbour(state, dir):
    # Find the empty tile and copy the state
    empty_i = state.index(0)
    next = state.copy()

    # Move up if not in the top row
    if (dir == "Up") and (empty_i > 2):
        next[empty_i], next[empty_i-3] = next[empty_i-3], next[empty_i]

    # Move down if not in the bottom row
    elif (dir == "Down") and (empty_i < 6):
        next[empty_i], next[empty_i+3] = next[empty_i+3], next[empty_i]

    # Move left if not in the left column
    elif (dir == "Left") and (empty_i % 3 != 0):
        next[empty_i], next[empty_i-1] = next[empty_i-1], next[empty_i]

    # Move right if not in the right column
    elif (dir == "Right") and (empty_i % 3 != 2):
        next[empty_i], next[empty_i+1] = next[empty_i+1], next[empty_i]

    return next


def is_goal(state):
    # Check if the goal state is reached
    return state == [0, 1, 2, 3, 4, 5, 6, 7, 8]


def reconstruct_path(parent, state):
    path = []
    key = tuple(state)

    # Trace back from the goal to the start
    while parent[key] is not None:
        previous, direction = parent[key]
        path.append(direction)
        key = previous

    path.reverse()
    return path
