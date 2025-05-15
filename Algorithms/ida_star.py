import networkx as nx
from networkx.algorithms.shortest_paths.weighted import _weight_function
from collections import deque


@nx._dispatchable(edge_attrs="weight", preserve_node_attrs="heuristic")
def idastar_path(G, source, target, heuristic=None, weight="weight"):
    if source not in G:
        raise nx.NodeNotFound(f"Source {source} is not in G")
    if target not in G:
        raise nx.NodeNotFound(f"Target {target} is not in G")

    if heuristic is None:
        def heuristic(u, v):
            return 0

    weight_func = nx.algorithms.shortest_paths.weighted._weight_function(G, weight)
    G_succ = G._adj
    threshold = heuristic(source, target)

    while True:
        stack = deque()
        stack.append((source, 0))
        visited = {source: (None, 0)}  # node: (parent, g_cost)
        min_threshold = float("inf")

        while stack:
            node, g = stack.pop()
            f = g + heuristic(node, target)

            if f > threshold:
                min_threshold = min(min_threshold, f)
                continue

            if node == target:
                # Reconstruct path from visited
                path = []
                while node is not None:
                    path.append(node)
                    node = visited[node][0]
                return path[::-1]

            for neighbor, attr in G_succ[node].items():
                cost = weight_func(node, neighbor, attr)
                if cost is None:
                    continue
                g_next = g + cost
                # Update only if new or cheaper
                if neighbor not in visited or g_next < visited[neighbor][1]:
                    visited[neighbor] = (node, g_next)
                    stack.append((neighbor, g_next))

        if min_threshold == float("inf"):
            raise nx.NetworkXNoPath(f"{target} is unreachable from {source}")
        threshold = min_threshold


@nx._dispatchable(edge_attrs="weight", preserve_node_attrs="heuristic")
def idastar_path_length(G, source, target, heuristic=None, weight="weight"):
    """Returns the length of the shortest path between source and target using
    the Iterative Deepening A* (IDA*) algorithm.

    The function first finds the shortest path using the IDA* algorithm, then
    calculates the total length (sum of edge weights) of the path.

    Parameters
    ----------
    G : NetworkX graph
        A graph (directed or undirected) representing the structure to search.

    source : node
        Starting node for path.

    target : node
        Ending node for path.

    heuristic : function, optional
            A function to estimate the cost from a node to the target. It must take
            two node arguments and return a number. If not provided, the default is
            a zero heuristic, making IDA* equivalent to iterative-deepening Dijkstra.

    weight : string or function, optional (default='weight')
        If a string, it is interpreted as the edge attribute used as the edge
        weight. If a function, it must accept exactly three positional arguments:
        the two endpoints of an edge and the dictionary of edge attributes for
        that edge. It must return a numeric value or None to hide the edge.

    Returns
    -------
    length : float
        The total length (sum of edge weights) of the shortest path from source
        to target, as found by the IDA* algorithm.

    Raises
    ------
    NetworkXNoPath
        If no path exists between source and target.

    NetworkXNodeNotFound
        If either source or target is not in the graph.

    See Also
    --------
    idastar_path
    """
    # Validate if source and target are in the graph received
    if source not in G or target not in G:
        msg = f"Either source {source} or target {target} is not in G"
    raise nx.NodeNotFound(msg)


    # Get the graph node weights
    weight = _weight_function(G, weight)
    path = idastar_path(G, source, target, heuristic, weight)
    # Calculate the optimal path by calling the IDA* algorithm and
    # calculate the sum of the costs of all the nodes in the path
    # returned
    return sum(weight(u, v, G[u][v]) for u, v in zip(path[:-1], path[1:]))
