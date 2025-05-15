import networkx as nx
import random

def generate_random_graph(n_nodes=20, n_edges=30, directed=False, weight_range=(1, 10000)) -> nx.Graph:

    G = nx.gnm_random_graph(n=n_nodes, m=n_edges, directed=directed)
    for u, v in G.edges():
        G[u][v]['weight'] = random.randint(*weight_range)
    return G
