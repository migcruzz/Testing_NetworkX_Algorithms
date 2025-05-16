import matplotlib.pyplot as plt
import networkx as nx

# Global configuration
GRAPH_FIGSIZE = (24, 14)
NODE_SIZE = 500
FONT_SIZE = 12
EDGE_LABEL_FONT_SIZE = 9
METRIC_FONT_SIZE = 30
METRIC_TITLE_SIZE = 50
AXIS_TITLE_SIZE = 20

class GraphPlotter:
    def __init__(self, graph: nx.Graph, seed: int = 42):
        self.graph = graph
        self.seed = seed
        self.pos = self._normalized_layout(graph, seed)

    def _safe_weight(self, u, v, default=0):
        data = self.graph.get_edge_data(u, v) or self.graph.get_edge_data(v, u)
        return data["weight"] if data else default

    def _normalized_layout(self, G: nx.Graph, seed=42):
        try:
            pos = nx.spring_layout(G, seed=seed)
        except TypeError:
            pos = nx.spring_layout(G, random_state=seed)

        xs, ys = zip(*pos.values())
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        range_x = max_x - min_x or 1.0
        range_y = max_y - min_y or 1.0

        return {
            node: ((x - min_x) / range_x, (y - min_y) / range_y)
            for node, (x, y) in pos.items()
        }

    def draw(
            self,
            source=None,
            target=None,
            path=None,
            metrics=None,
            output_path=None,
    ):
        fig, axs = plt.subplots(1, 2, figsize=GRAPH_FIGSIZE, gridspec_kw={'width_ratios': [4, 1]})

        ax = axs[0]
        plt.sca(ax)
        nx.draw(
            self.graph,
            self.pos,
            with_labels=True,
            node_color="lightblue",
            edge_color="gray",
            node_size=NODE_SIZE,
            font_size=FONT_SIZE,
        )
        nx.draw_networkx_edge_labels(
            self.graph,
            self.pos,
            edge_labels={
                e: f"{w:.1f}" for e, w in nx.get_edge_attributes(self.graph, "weight").items()
            },
            font_size=EDGE_LABEL_FONT_SIZE,
        )

        if source in self.graph:
            nx.draw_networkx_nodes(self.graph, self.pos, nodelist=[source], node_color="green", node_size=NODE_SIZE + 100)
        if target in self.graph:
            nx.draw_networkx_nodes(self.graph, self.pos, nodelist=[target], node_color="red", node_size=NODE_SIZE + 100)

        total_cost = 0
        if path and len(path) > 1:
            path_edges = list(zip(path, path[1:]))
            total_cost = sum(self._safe_weight(u, v) for u, v in path_edges)
            nx.draw_networkx_edges(self.graph, self.pos, edgelist=path_edges, width=2.5, edge_color="red")

        title = (
            f"Path from {source} to {target} | Total cost: {total_cost:.2f}"
            if path else "Graph"
        )
        ax.set_title(title, fontsize=AXIS_TITLE_SIZE)
        ax.set_axis_off()

        ax = axs[1]
        ax.axis('off')
        ax.set_title("Metrics", fontweight='bold', fontsize=METRIC_TITLE_SIZE)

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
                return str(v)

            lines = [
                f"{k:<25}: {format_value(k, v)}"
                for k, v in metrics.items()
            ]
            ax.text(0.05, 1, "\n".join(lines), va='top', ha='left', fontsize=METRIC_FONT_SIZE, family='monospace')

        if output_path:
            plt.savefig(output_path, bbox_inches="tight")
            plt.close()
        else:
            plt.tight_layout()
            plt.show()
