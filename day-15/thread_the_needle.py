import numpy as np
import typing as T


def parse_input(filename: str) -> np.ndarray:
    with open(filename, 'r') as fp:
        data = [
            [x for x in map(int, line.strip())]
            for line in fp.readlines()
        ]
    return np.array(data, dtype='uint8')


def least_cost_route(node_cost: np.ndarray) -> np.ndarray:
    
    # init
    shape = node_cost.shape
    size = node_cost.size
    start_idx = (0, 0)
    end_idx = (shape[0]-1, shape[1]-1)
    nbr_offsets = np.array([[-1, 0], [0, 1], [1, 0], [0, -1]], dtype=np.int8)

    path_cost = np.full(shape, np.inf, dtype=np.single)
    upstream_row = np.full(shape, 0, dtype=np.short)
    upstream_col = np.full(shape, 0, dtype=np.short)
    linear_idx = np.reshape(np.arange(size), shape)
    unvisited = np.full(shape, True, dtype=np.bool_)


    def neighbors(index: np.ndarray) -> T.List[T.Tuple[int, int]]:
        x = np.array(index) + nbr_offsets
        valid = np.logical_and(np.all(x >= 0, axis=1), np.all(x <= end_idx, axis=1))
        return [tuple(y) for y in x[valid, :]]
        

    def next_idx():
        min_cost_index = np.argmin(path_cost[unvisited])
        return tuple(
            np.unravel_index(
                linear_idx[unvisited].flat[min_cost_index],
                shape
            )
        )        


    # start at the beginning
    idx = start_idx
    path_cost[idx] = node_cost[idx] 

    # find the shortest path from the start to all nodes
    # note: we could stop when we first arrive at the end node, meh.
    while True:
        
        unvisited[idx] = False 

        for nbr_idx in neighbors(idx):

            if unvisited[nbr_idx]:

                candidate_cost = path_cost[idx] + node_cost[nbr_idx]
                
                if candidate_cost < path_cost[nbr_idx]:
                    path_cost[nbr_idx] = candidate_cost
                    upstream_row[nbr_idx] = idx[0]
                    upstream_col[nbr_idx] = idx[1]

        # select the next node
        idx = next_idx()

        # check exit condition
        if idx == end_idx:
            break

    # walk back the path from end to start
    path = np.zeros(shape, dtype=np.bool_)
    idx = end_idx

    while idx != start_idx:
        path[idx] = True
        idx = (upstream_row[idx], upstream_col[idx])

    return path


def total_cost(node_cost: np.ndarray, path: np.ndarray) -> int:
    return np.sum(node_cost[path])
    

def tile(template: np.ndarray) -> np.ndarray:

    def _increment(x: np.ndarray):
        return np.maximum(1, (1 + x) % 10)

    tiles = [template]
    for _ in range(1, 5):
        tiles.append(_increment(tiles[-1]))
    
    template = np.concatenate(tiles, axis=1)

    tiles = [template]
    for _ in range(1, 5):
        tiles.append(_increment(tiles[-1]))

    return np.concatenate(tiles, axis=0)



def main(input_file: str):

    print('puzzle 1 ----------')
    costs = parse_input(input_file)
    route = least_cost_route(costs)
    route_cost = total_cost(costs, route)
    print(f'Shortest path risk is: {route_cost}')
    print()

    print('puzzle 2 ----------')
    tiled_costs = tile(costs)
    tiled_route = least_cost_route(tiled_costs)
    tiled_route_cost = total_cost(tiled_costs, tiled_route)
    print(f'Shortest tiled path risk is: {tiled_route_cost}')
    print()


if __name__ == '__main__':

    
    input_file = 'test_input.txt'
    # input_file = 'input.txt'

    main(input_file)


