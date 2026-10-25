def div_mod(number:int):
    return (number//3 , number%3)


def manhattan(state:list):
    distance = 0
    for i , tile in enumerate(state):
        if tile == 0 : continue
        target_row , target_col = div_mod(tile)
        current_row , current_col = div_mod(i)
        distance += abs(target_col - current_col) + abs(target_row - current_row)
    return distance

def euclidean(state):
    distance = 0
    for i , tile in enumerate(state):
        if tile == 0 : continue
        target_row , target_col = div_mod(tile)
        current_row , current_col = div_mod(i)
        distance += ((target_col - current_col)**2 + (target_row - current_row)**2)**0.5
    return distance
