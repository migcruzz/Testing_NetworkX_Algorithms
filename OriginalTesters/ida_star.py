from itertools import pairwise

from Algorithms.ida_star import idastar_path, idastar_path_length
import networkx as nx

"""IDA* TESTING"""


def test_multiple_optimal_paths_idastar(self):
    """Tests that IDA* algorithm finds any of multiple optimal paths"""
    heuristic_values = {"a": 1.35, "b": 1.18, "c": 0.67, "d": 0}

    def h(u, v):
        return heuristic_values[u]

    graph = nx.Graph()
    points = ["a", "b", "c", "d"]
    edges = [("a", "b", 0.18), ("a", "c", 0.68), ("b", "c", 0.50), ("c", "d", 0.67)]

    graph.add_nodes_from(points)
    graph.add_weighted_edges_from(edges)

    path1 = ["a", "c", "d"]
    path2 = ["a", "b", "c", "d"]
    assert idastar_path(graph, "a", "d", h) in (path1, path2)


def test_idastar_directed(self):
    assert idastar_path(self.XG, "s", "v") == ["s", "x", "u", "v"]


def test_idastar_directed_weight_function(self):
    def w1(u, v, d):
        return d["weight"]

    assert idastar_path(self.XG, "x", "u", weight=w1) == ["x", "u"]
    assert idastar_path_length(self.XG, "x", "u", weight=w1) == 3
    assert idastar_path(self.XG, "s", "v", weight=w1) == ["s", "x", "u", "v"]
    assert idastar_path_length(self.XG, "s", "v", weight=w1) == 9

    def w2(u, v, d):
        return None if (u, v) == ("x", "u") else d["weight"]

    assert idastar_path(self.XG, "x", "u", weight=w2) == ["x", "y", "s", "u"]
    assert idastar_path_length(self.XG, "x", "u", weight=w2) == 19
    assert idastar_path(self.XG, "s", "v", weight=w2) == ["s", "x", "v"]
    assert idastar_path_length(self.XG, "s", "v", weight=w2) == 10

    def w3(u, v, d):
        return d["weight"] + 10

    assert idastar_path(self.XG, "x", "u", weight=w3) == ["x", "u"]
    assert idastar_path_length(self.XG, "x", "u", weight=w3) == 13
    assert idastar_path(self.XG, "s", "v", weight=w3) == ["s", "x", "v"]
    assert idastar_path_length(self.XG, "s", "v", weight=w3) == 30


def test_idastar_multigraph(self):
    G = nx.MultiDiGraph(self.XG)
    G.add_weighted_edges_from((u, v, 1000) for (u, v) in list(G.edges()))
    assert idastar_path(G, "s", "v") == ["s", "x", "u", "v"]
    assert idastar_path_length(G, "s", "v") == 9


def test_idastar_undirected(self):
    GG = self.XG.to_undirected()
    # make sure we get lower weight
    # to_undirected might choose either edge with weight 2 or weight 3
    GG["u"]["x"]["weight"] = 2
    GG["y"]["v"]["weight"] = 2
    assert idastar_path(GG, "s", "v") == ["s", "x", "u", "v"]
    assert idastar_path_length(GG, "s", "v") == 8


def test_idastar_directed2(self):
    XG2 = nx.DiGraph()
    edges = [
        (1, 4, 1),
        (4, 5, 1),
        (5, 6, 1),
        (6, 3, 1),
        (1, 3, 50),
        (1, 2, 100),
        (2, 3, 100),
    ]
    XG2.add_weighted_edges_from(edges)
    assert idastar_path(XG2, 1, 3) == [1, 4, 5, 6, 3]


def test_idastar_undirected2(self):
    XG3 = nx.Graph()
    edges = [(0, 1, 2), (1, 2, 12), (2, 3, 1), (3, 4, 5), (4, 5, 1), (5, 0, 10)]
    XG3.add_weighted_edges_from(edges)
    assert idastar_path(XG3, 0, 3) == [0, 1, 2, 3]
    assert idastar_path_length(XG3, 0, 3) == 15


def test_idastar_undirected3(self):
    XG4 = nx.Graph()
    edges = [
        (0, 1, 2),
        (1, 2, 2),
        (2, 3, 1),
        (3, 4, 1),
        (4, 5, 1),
        (5, 6, 1),
        (6, 7, 1),
        (7, 0, 1),
    ]
    XG4.add_weighted_edges_from(edges)
    assert idastar_path(XG4, 0, 2) == [0, 1, 2]
    assert idastar_path_length(XG4, 0, 2) == 4


""" Tests that IDA* finds correct path when multiple paths exist
    and the best one is not expanded first (GH issue #3464)
"""


def test_idastar_w1(self):
    G = nx.DiGraph()
    G.add_edges_from(
        [
            ("s", "u"),
            ("s", "x"),
            ("u", "v"),
            ("u", "x"),
            ("v", "y"),
            ("x", "u"),
            ("x", "w"),
            ("w", "v"),
            ("x", "y"),
            ("y", "s"),
            ("y", "v"),
        ]
    )
    assert idastar_path(G, "s", "v") == ["s", "u", "v"]
    assert idastar_path_length(G, "s", "v") == 2


def test_idastar_nopath(self):
    with pytest.raises(nx.NodeNotFound):
        idastar_path(self.XG, "s", "moon")


def test_idastar_inadmissible_heuristic_with_cutoff(self):
    heuristic_values = {"s": 36, "y": 14, "x": 10, "u": 10, "v": 0}

    def h(u, v):
        return heuristic_values[u]

    # optimal path_length in XG is 9. This heuristic gives over-estimate.
    assert idastar_path_length(self.XG, "s", "v", heuristic=h) == 10


def test_cycle_idastar(self):
    C = nx.cycle_graph(7)
    assert idastar_path(C, 0, 3) == [0, 1, 2, 3]
    assert nx.dijkstra_path(C, 0, 4) == [0, 6, 5, 4]


def test_idastar_NetworkXNoPath(self):
    """Tests that exception is raised when there exists no
    path between source and target"""
    G = nx.gnp_random_graph(10, 0.2, seed=10)
    with pytest.raises(nx.NetworkXNoPath):
        idastar_path(G, 4, 9)


def test_idastar_NodeNotFound(self):
    """Tests that exception is raised when either
    source or target is not in graph"""
    G = nx.gnp_random_graph(10, 0.2, seed=10)
    with pytest.raises(nx.NodeNotFound):
        idastar_path_length(G, 11, 9)


def test_idastar_tuple_nodes(self):
    G = nx.grid_graph(dim=[3, 3])  # nodes are two-tuples (x,y)
    nx.set_edge_attributes(G, {e: e[1][0] * 2 for e in G.edges()}, "cost")

    def dist(a, b):
        (x1, y1) = a
        (x2, y2) = b
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

    assert idastar_path(G, (0, 0), (2, 2), heuristic=dist, weight="cost") == [
        (0, 0),
        (0, 1),
        (0, 2),
        (1, 2),
        (2, 2),
    ]
