import matplotlib.pyplot as plt
import networkx as nx


def _safe_weight(G: nx.Graph, u, v, default=0):
    data = G.get_edge_data(u, v) or G.get_edge_data(v, u)
    return data["weight"] if data else default


def draw_graph(G: nx.Graph, source=None, target=None, path=None, metrics=None, output_path=None):
    fig, axs = plt.subplots(1, 2, figsize=(17, 9), gridspec_kw={'width_ratios': [4, 1]})
    pos = nx.spring_layout(G, seed=42, k=2.0)

    # Plot graph
    ax = axs[0]
    plt.sca(ax)
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_color="lightblue",
        edge_color="gray",
        node_size=300,
        font_size=10,
    )
    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels={e: f"{w:.1f}" for e, w in nx.get_edge_attributes(G, "weight").items()},
        font_size=8,
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
        if path else "Generated Graph"
    )
    ax.set_title(title, fontsize=14)

    ax = axs[1]
    ax.axis('off')
    ax.set_title("Metrics", fontweight='bold', fontsize=16)

    if metrics:
        def format_value(k, v):
            if isinstance(v, float):
                if "Time" in k:
                    return f"{v:.6f} s"
                elif "Memory" in k:
                    return f"{v:.6f} MiB"
                elif "Cost" in k:
                    return f"{v:.0f}"
                else:
                    return f"{v:.6f}"
            return v

        lines = [
            f"{k:<25}: {format_value(k, v)}"
            for k, v in metrics.items()
        ]
        text = "\n".join(lines)
        ax.text(0.05, 1, text, va='top', ha='left', fontsize=13, family='monospace')

    if output_path:
        plt.savefig(output_path, bbox_inches="tight")
        plt.close()
    else:
        plt.tight_layout()
        plt.show()
