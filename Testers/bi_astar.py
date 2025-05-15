import random
import statistics
import time
import tracemalloc

import networkx as nx
from tabulate import tabulate

from Algorithms.bi_astar import bidirectional_astar


class AStarVsBidirectionalComparison:
    def __init__(self, graph: nx.Graph, source, target, n_modifications=50):
        self.graph = graph
        self.source = source
        self.target = target
        self.name = "Bidirectional A*"
        self.n_modifications = n_modifications

    def compute_cost(self, path):
        return sum(self.graph[path[i]][path[i + 1]]["weight"] for i in range(len(path) - 1))

    def compare_time(self):
        t0 = time.perf_counter()
        path_astar = nx.astar_path(self.graph, self.source, self.target, weight="weight")
        t1 = time.perf_counter()
        time_astar = t1 - t0
        cost_astar = self.compute_cost(path_astar)

        t0 = time.perf_counter()
        cost_bi, path_bi, _ = bidirectional_astar(self.graph, self.source, self.target)
        t1 = time.perf_counter()
        time_bi = t1 - t0

        return {
            "A* Time (s)": time_astar,
            "Bidirectional A* Time (s)": time_bi,
            "A* Cost": cost_astar,
            "Bidirectional A* Cost": cost_bi,
        }

    def compare_memory(self, runs: int = 5):
        peaks_astar = []
        peaks_bi = []

        for _ in range(runs):
            tracemalloc.start()
            nx.astar_path(self.graph, self.source, self.target, weight="weight")
            _, peak_a = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            peaks_astar.append(peak_a)

            tracemalloc.start()
            bidirectional_astar(self.graph, self.source, self.target)
            _, peak_b = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            peaks_bi.append(peak_b)

        mib = 1024 * 1024
        return {
            "A* Peak Memory (MiB)": max(peaks_astar) / mib,
            "A* Avg Memory (MiB)": statistics.mean(peaks_astar) / mib,
            "Bi-A* Peak Memory (MiB)": max(peaks_bi) / mib,
            "Bi-A* Avg Memory (MiB)": statistics.mean(peaks_bi) / mib,
        }

    def compare_recalculation(self):
        neighbor = next(iter(self.graph[self.source]))
        self.graph[self.source][neighbor]["weight"] += 1

        t0 = time.perf_counter()
        nx.astar_path(self.graph, self.source, self.target, weight="weight")
        t1 = time.perf_counter()
        time_astar = t1 - t0

        t0 = time.perf_counter()
        bidirectional_astar(self.graph, self.source, self.target)
        t1 = time.perf_counter()
        time_bi = t1 - t0

        return {
            "A* Recalc Time (s)": time_astar,
            "Bidirectional A* Recalc Time (s)": time_bi,
        }

    def compare_bulk_modifications(self):
        all_edges = list(self.graph.edges)
        times_astar = []
        times_bi = []

        for _ in range(self.n_modifications):
            u, v = random.choice(all_edges)
            new_w = random.randint(5, 50)
            self.graph[u][v]["weight"] = new_w

            t0 = time.perf_counter()
            nx.astar_path(self.graph, self.source, self.target, weight="weight")
            t1 = time.perf_counter()
            times_astar.append(t1 - t0)

            t0 = time.perf_counter()
            bidirectional_astar(self.graph, self.source, self.target)
            t1 = time.perf_counter()
            times_bi.append(t1 - t0)

        return {
            "A* Bulk Avg Time (s)": statistics.mean(times_astar),
            "Bidirectional A* Bulk Avg Time (s)": statistics.mean(times_bi),
            "Bulk Modifications Count": self.n_modifications
        }

    def run_all(self):
        time_data = self.compare_time()
        mem_data = self.compare_memory()
        recalc_data = self.compare_recalculation()
        bulk_data = self.compare_bulk_modifications()

        result = {**time_data, **mem_data, **recalc_data, **bulk_data}
        table = [[k, f"{v:.6f}" if isinstance(v, float) else v] for k, v in result.items()]
        print(tabulate(table, headers=["Metric", "Value"], tablefmt="grid"))
        return result
