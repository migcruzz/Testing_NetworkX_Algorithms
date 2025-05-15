import statistics
import time

import networkx as nx
from memory_profiler import memory_usage
from tabulate import tabulate

from Algorithms.bi_astar import bidirectional_astar


class AStarVsBidirectionalComparison:
    def __init__(self, graph: nx.Graph, source, target):
        self.graph = graph
        self.source = source
        self.target = target

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

    def compare_memory(self):
        def run_astar():
            nx.astar_path(self.graph, self.source, self.target, weight="weight")

        def run_bi_astar():
            bidirectional_astar(self.graph, self.source, self.target)

        max_mem_astar = max(memory_usage(run_astar, max_iterations=1))
        max_mem_bi = max(memory_usage(run_bi_astar, max_iterations=1))

        mean_mem_astar = statistics.mean(memory_usage(run_astar, max_iterations=1))
        mean_mem_bi = statistics.mean(memory_usage(run_bi_astar, max_iterations=1))

        return {
            "MAX A* Memory (MiB)": max_mem_astar,
            "MIN Bidirectional A* Memory (MiB)": max_mem_bi,
            "MEAN A* Memory (MiB)": mean_mem_astar,
            "MEAN Bidirectional A* Memory (MiB)": mean_mem_bi,
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

    def run_all(self):
        time_data = self.compare_time()
        mem_data = self.compare_memory()
        recalc_data = self.compare_recalculation()

        result = {**time_data, **mem_data, **recalc_data}
        table = [[k, f"{v:.6f}" if isinstance(v, float) else v] for k, v in result.items()]
        print(tabulate(table, headers=["Metric", "Value"], tablefmt="grid"))
        return result
