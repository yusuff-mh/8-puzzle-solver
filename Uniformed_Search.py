from collections import deque
from puzzle import *


def bfs(state):
    # BFS explores states level by level using a queue
    frontier = deque([state])

    # Store each state's parent and the move used to reach it
    # The initial state has no parent
    parent = {tuple(state): None}

    # Store the depth of each node
    depths = {tuple(state): 0}

    expanded_counter = 0
    max_depth_reached = 0
    directions = ["Up", "Down", "Left", "Right"]

    while frontier:
        # Remove the oldest state from the queue
        current = frontier.popleft()

        current_tuple = tuple(current)
        current_depth = depths[current_tuple]

        # Update the maximum depth
        if current_depth > max_depth_reached:
            max_depth_reached = current_depth

        # Stop when the goal state is reached
        if is_goal(current):
            path = reconstruct_path(parent, current)
            return path, expanded_counter, len(path), max_depth_reached

        expanded_counter += 1
        # Generate all valid neighbouring states
        for direction in directions:
            neighbour = find_neighbour(current, direction)
            key = tuple(neighbour)

            # Add only states that have not been discovered before
            if key not in parent:
                parent[key] = (current_tuple, direction)
                depths[key] = current_depth + 1
                frontier.append(neighbour)

    # Return None if no solution is found
    return None, expanded_counter, 0, max_depth_reached


def dfs(state):
    # DFS uses a stack to explore one branch deeply before backtracking
    frontier = [state]

    parent = {tuple(state): None}

    depths = {tuple(state): 0}

    expanded_counter = 0
    max_depth_reached = 0
    directions = ["Up", "Down", "Left", "Right"]

    while frontier:
        # Remove the most recently added state
        current = frontier.pop()

        current_tuple = tuple(current)
        current_depth = depths[current_tuple]
        
        # Update the maximum depth
        if current_depth > max_depth_reached:
            max_depth_reached = current_depth

        if is_goal(current):
            path = reconstruct_path(parent, current)
            return path, expanded_counter, len(path), max_depth_reached
        
        expanded_counter += 1
        for direction in reversed(directions):
            neighbour = find_neighbour(current, direction)
            key = tuple(neighbour)

            # Prevent revisiting states already discovered
            if key not in parent:
                parent[key] = (current_tuple, direction)
                depths[key] = current_depth + 1
                frontier.append(neighbour)

    return None, expanded_counter, 0, max_depth_reached

def dls(start, limit):
    # Convert the initial state to a tuple to use it as a dictionary key
    start_tuple = tuple(start)

    # Stack stores (state, depth)
    frontier = [(start, 0)]

    # Store each state's parent and the direction used to reach it
    parent = {start_tuple: None}

    # Store the minimum depth at which each state has been visited
    visited = {start_tuple: 0}

    expanded_count = 0
    directions = ["Up", "Down", "Left", "Right"]

    while frontier:
        # Get the last state added to the stack (DFS behavior)
        current, depth = frontier.pop()
        current_tuple = tuple(current)

        # Skip outdated entries reached at a greater depth
        if depth != visited[current_tuple]:
            continue

        # Check whether the current state is the goal
        if is_goal(current):
            return reconstruct_path(parent, current), expanded_count

        # Do not expand states that reach the depth limit
        if depth >= limit:
            continue

        expanded_count += 1

        # Generate valid neighbouring states
        for direction in reversed(directions):
            neighbour = find_neighbour(current, direction)

            # Skip invalid moves
            if neighbour is None:
                continue

            key = tuple(neighbour)
            new_depth = depth + 1

            # Ignore states that exceed the depth limit
            if new_depth > limit:
                continue

            # Skip states already reached at an equal or smaller depth
            if key in visited and visited[key] <= new_depth:
                continue

            # Record the new depth and the parent information
            visited[key] = new_depth
            parent[key] = (current_tuple, direction)

            # Add the neighbour to the stack
            frontier.append((neighbour, new_depth))

    # No solution was found within the given depth limit
    return None, expanded_count

def ids(state):
    limit = 0
    total_expanded = 0
    # Store the expanded count for the previous iteration
    prev_expanded_count = -1

    while True:
        path, expanded_count = dls(state, limit)

        # Count expansions across all iterations
        total_expanded += expanded_count

        # Return when a solution is found
        if path is not None:
            return path, total_expanded, len(path), limit

        # if the maximum depth has reached, the search failed
        if expanded_count == prev_expanded_count:
            return None, total_expanded, 0, limit

        prev_expanded_count = expanded_count

        # Increase the maximum allowed depth and search again
        limit += 1