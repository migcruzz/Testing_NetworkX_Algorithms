#!/usr/bin/env python3
"""
Generate a random directed graph with weights, save it as CSV,
and produce an interactive HTML visualization (pan/zoom) using pure NetworkX + mpld3.
"""

import networkx as nx
import pandas as pd
import random
import matplotlib.pyplot as plt
import mpld3

def main():
    # 1) Parameters
    N_NODES = 20
    N_EDGES = 40
    CSV_PATH = "graph.csv"
    HTML_PATH = "interactive_graph.html"
    RANDOM_SEED = 42

    # 2) Build random directed graph
    G = nx.gnm_random_graph(n=N_NODES, m=N_EDGES, directed=True, seed=RANDOM_SEED)
    for u, v in G.edges():
        G[u][v]['weight'] = round(random.uniform(1, 10), 2)

    # 3) Export to CSV
    df = nx.to_pandas_edgelist(G)
    df.to_csv(CSV_PATH, index=False)
    print(f"Saved edge list to {CSV_PATH}")

    # 4) Compute node positions once
    pos = nx.spring_layout(G, seed=RANDOM_SEED)

    # 5) Draw the graph with matplotlib
    fig, ax = plt.subplots(figsize=(8, 6))
    nx.draw_networkx_nodes(
        G, pos,
        ax=ax,
        node_size=300,
        node_color="skyblue"
    )
    nx.draw_networkx_labels(
        G, pos,
        ax=ax,
        font_size=8
    )
    nx.draw_networkx_edges(
        G, pos,
        ax=ax,
        arrowstyle="->",
        arrowsize=10
    )

    # 6) Draw edge weight labels
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(
        G, pos,
        edge_labels=edge_labels,
        ax=ax,
        font_color='red',
        font_size=7
    )

    ax.set_title("Interactive Directed Graph with Weights")
    ax.axis('off')
    plt.tight_layout()

    # 7) Save interactive HTML
    mpld3.save_html(fig, HTML_PATH)
    print(f"Saved interactive HTML visualization to {HTML_PATH}")

if __name__ == "__main__":
    main()
