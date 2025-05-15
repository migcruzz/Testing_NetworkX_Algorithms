import matplotlib.pyplot as plt
import networkx as nx

def draw_graph(G: nx.Graph, source=None, target=None, path=None, output_path=None):
    plt.figure(figsize=(16, 10))
    pos = nx.spring_layout(G, seed=42, k=2.0)
    weights = nx.get_edge_attributes(G, 'weight')

    nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray',
            node_size=300, font_size=8)
    nx.draw_networkx_edge_labels(G, pos, edge_labels={k: f"{v:.1f}" for k, v in weights.items()}, font_size=6)

    if source in G:
        nx.draw_networkx_nodes(G, pos, nodelist=[source], node_color='green', node_size=400)
    if target in G:
        nx.draw_networkx_nodes(G, pos, nodelist=[target], node_color='red', node_size=400)

    path_cost = 0
    if path and len(path) > 1:
        path_edges = list(zip(path, path[1:]))
        path_cost = sum(G[u][v]['weight'] for u, v in path_edges)
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, width=2.5, edge_color='red')

    title = f"Path from {source} to {target} | Total cost: {path_cost:.2f}" if path else "Generated Graph"
    plt.title(title)

    if output_path:
        plt.savefig(output_path)
        plt.close()
    else:
        plt.tight_layout()
        plt.show()
