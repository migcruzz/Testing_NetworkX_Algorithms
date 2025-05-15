import matplotlib.pyplot as plt
import networkx as nx


def _safe_weight(G: nx.Graph, u, v, default=0):
    data = G.get_edge_data(u, v) or G.get_edge_data(v, u)
    return data["weight"] if data else default


def draw_graph(G: nx.Graph, source=None, target=None, path=None, output_path=None):
    plt.figure(figsize=(16, 10))
    pos = nx.spring_layout(G, seed=42, k=2.0)

    nx.draw(
        G,
        pos,
        with_labels=True,
        node_color="lightblue",
        edge_color="gray",
        node_size=300,
        font_size=8,
    )
    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels={e: f"{w:.1f}" for e, w in nx.get_edge_attributes(G, "weight").items()},
        font_size=6,
    )

    if source in G:
        nx.draw_networkx_nodes(G, pos, nodelist=[source], node_color="green", node_size=400)
    if target in G:
        nx.draw_networkx_nodes(G, pos, nodelist=[target], node_color="red", node_size=400)

    total_cost = 0
    if path and len(path) > 1:
        path_edges = list(zip(path, path[1:]))
        total_cost = sum(_safe_weight(G, u, v) for u, v in path_edges)
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, width=2.5, edge_color="red")

    title = (
        f"Path from {source} to {target} | Total cost: {total_cost:.2f}"
        if path
        else "Generated Graph"
    )
    plt.title(title)

    if output_path:
        plt.savefig(output_path, bbox_inches="tight")
        plt.close()
    else:
        plt.tight_layout()
        plt.show()
