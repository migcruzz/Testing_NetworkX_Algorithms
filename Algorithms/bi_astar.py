"""Shortest paths and path lengths using the A* ("A star") algorithm."""

import heapq
import math
from functools import cache
from itertools import count

import networkx as nx
from networkx.algorithms.shortest_paths.weighted import _weight_function
from networkx.exception import NetworkXNoPath, NodeNotFound
from networkx.utils.decorators import not_implemented_for

__all__ = ["bidirectional_astar"]


# === Bidirectional A* Search ===


@not_implemented_for("multigraph")
@nx._dispatchable(edge_attrs="weight", preserve_node_attrs="heuristic")
def bidirectional_astar(
        G,
        source,
        target,
        heuristic=None,
        weight="weight",
        max_nodes_expanded=None,
        max_heuristic_distance=None,
        greedy=False,
):
    """Returns a shortest path between source and target using Bidirectional A*.

    This implementation performs two simultaneous A* searches—one forward from the
    source, one backward from the target—until the frontiers meet.

    Parameters
    ----------
    G : NetworkX graph

    source : node
        Starting node for path

    target : node
        Ending node for path

    heuristic : function, optional
        A function to estimate the distance from a node to the target.
        Takes two node arguments and returns a float. If None, defaults
        to Euclidean heuristic for 2D grid graphs.

    weight : string or function, default="weight"
        Edge weight specification. If a string, edge weights are accessed
        via `G[u][v][weight]`. If a function, it should accept arguments
        (u, v, edge_data) and return a numeric cost.

    max_nodes_expanded : int, optional
        If set, defines a maximum number of nodes to expand. When exceeded,
        switches to greedy mode to finish faster.

    max_heuristic_distance : float, optional
        If set, the algorithm aborts if estimated heuristic distance
        between source and target exceeds this threshold.

    greedy : bool, default=False
        If True, the algorithm uses only the heuristic (Greedy Best-First Search),
        ignoring accumulated cost. Provides faster execution at the cost of
        path optimality.

    Returns
    -------
    total_cost : float
        The total weight of the path found.

    path : list
        List of nodes representing the computed path from source to target.

    stats : dict
        Dictionary with profiling statistics:
        - nodes_expanded_forward
        - nodes_expanded_backward
        - total_nodes_expanded
        - explored_percent

    Raises
    ------
    NetworkXNoPath
        If no path exists between source and target.

    Notes
    -----
    This implementation prioritizes performance in large graphs.
    If `greedy=True`, the path may not be optimal.

    """
    if source not in G:
        raise NodeNotFound(f"Source {source} is not in G")
    if target not in G:
        raise NodeNotFound(f"Target {target} is not in G")
    if source == target:
        return (0, [source], {"total_nodes_expanded": 1})

    # Default heuristic: Euclidean distance between 2D grid coordinates
    @cache
    def _euclidean_heuristic(u, v):
        try:
            x1, y1 = u
            x2, y2 = v
            return math.hypot(x2 - x1, y2 - y1)
        except (TypeError, ValueError):
            return 0

    if heuristic is None:
        heuristic = _euclidean_heuristic

    def h_forward(n):
        return heuristic(n, target)

    def h_backward(n):
        return heuristic(n, source)

    weight_fn = _weight_function(G, weight)

    dist = [{}, {}]
    pred = [{}, {}]
    seen = [{source: 0}, {target: 0}]
    fringe = [[], []]
    counter = count()
    visited_nodes = [set(), set()]
    frontier_sizes = []

    heapq.heappush(
        fringe[0],
        ((h_forward(source) if greedy else h_forward(source)), next(counter), source),
    )
    heapq.heappush(
        fringe[1],
        ((h_backward(target) if greedy else h_backward(target)), next(counter), target),
    )

    neighbors = [G._succ, G._pred] if G.is_directed() else [G._adj, G._adj]
    meeting_node = None

    while fringe[0] and fringe[1]:
        f_cost_0 = fringe[0][0][0]
        f_cost_1 = fringe[1][0][0]
        direction = 0 if f_cost_0 <= f_cost_1 else 1

        f_cost, _, curr = heapq.heappop(fringe[direction])
        if curr in dist[direction]:
            continue

        dist[direction][curr] = seen[direction][curr]
        visited_nodes[direction].add(curr)

        if curr in seen[1 - direction]:
            meeting_node = curr
            break

        if (
                max_heuristic_distance is not None
                and heuristic(source, target) > max_heuristic_distance
        ):
            raise NetworkXNoPath("Path exceeds max heuristic distance.")

        if (
                max_nodes_expanded is not None
                and (len(visited_nodes[0]) + len(visited_nodes[1])) > max_nodes_expanded
        ):
            greedy = True  # force fast greedy fallback

        frontier_sizes.append((len(fringe[0]), len(fringe[1])))

        for nbr, edata in neighbors[direction][curr].items():
            cost = (
                weight_fn(curr, nbr, edata)
                if direction == 0
                else weight_fn(nbr, curr, edata)
            )
            if cost is None:
                continue
            new_cost = dist[direction][curr] + (0 if greedy else cost)
            if nbr in dist[direction]:
                continue
            if nbr not in seen[direction] or new_cost < seen[direction][nbr]:
                seen[direction][nbr] = new_cost
                pred[direction][nbr] = curr
                heuristic_cost = h_forward(nbr) if direction == 0 else h_backward(nbr)
                total_cost = heuristic_cost if greedy else new_cost + heuristic_cost
                heapq.heappush(fringe[direction], (total_cost, next(counter), nbr))

    if meeting_node is None:
        raise NetworkXNoPath(f"No path between {source} and {target}.")

    forward_path = []
    node = meeting_node
    while node in pred[0]:
        forward_path.append(node)
        node = pred[0][node]
    forward_path.append(node)
    forward_path.reverse()

    backward_path = []
    node = meeting_node
    while node in pred[1]:
        backward_path.append(node)
        node = pred[1][node]
    backward_path.append(node)

    forward_path.pop()
    full_path = forward_path + backward_path

    stats = {
        "nodes_expanded_forward": len(visited_nodes[0]),
        "nodes_expanded_backward": len(visited_nodes[1]),
        "total_nodes_expanded": len(visited_nodes[0]) + len(visited_nodes[1]),
        "explored_percent": (len(visited_nodes[0]) + len(visited_nodes[1]))
                            / G.number_of_nodes()
                            * 100,
    }

    total_cost = 0
    for i in range(len(full_path) - 1):
        u, v = full_path[i], full_path[i + 1]
        total_cost += G[u][v].get(weight, 1)

    return (total_cost, full_path, stats)
