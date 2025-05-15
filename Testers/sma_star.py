import time

import networkx as nx
from memory_profiler import memory_usage
from networkx.algorithms.shortest_paths.astar import astar_path
from tabulate import tabulate

from Algorithms.sma_star import sma_star_path


class SMAStarVsAStarComparison:
    def __init__(self, graph: nx.Graph, source, target, heuristic=None):
        self.graph = graph
        self.source = source
        self.target = target
        self.heuristic = heuristic

    def compute_cost(self, path):
        return sum(self.graph[path[i]][path[i + 1]]["weight"] for i in range(len(path) - 1))

    def compare_initial_time(self):
        t0 = time.perf_counter()
        path_astar = astar_path(self.graph, self.source, self.target, weight="weight")
        t1 = time.perf_counter()
        time_astar = t1 - t0
        cost_astar = self.compute_cost(path_astar)

        t0 = time.perf_counter()
        path_sma = sma_star_path(self.graph, self.source, self.target, heuristic=self.heuristic)
        t1 = time.perf_counter()
        time_sma = t1 - t0
        cost_sma = self.compute_cost(path_sma)

        return {
            "A* Time (s)": time_astar,
            "SMA* Time (s)": time_sma,
            "A* Cost": cost_astar,
            "SMA* Cost": cost_sma,
        }

    def compare_memory(self):
        def run_astar():
            astar_path(self.graph, self.source, self.target, weight="weight")

        def run_sma():
            sma_star_path(self.graph, self.source, self.target, heuristic=self.heuristic)

        mem_astar = max(memory_usage(run_astar, max_iterations=1, interval=0.001))
        mem_sma = max(memory_usage(run_sma, max_iterations=1, interval=0.001))

        return {
            "A* Memory (MiB)": mem_astar,
            "SMA* Memory (MiB)": mem_sma,
        }

    def compare_recalculation(self):
        neighbor = next(iter(self.graph[self.source]))
        self.graph[self.source][neighbor]["weight"] += 5

        t0 = time.perf_counter()
        astar_path(self.graph, self.source, self.target, weight="weight")
        t1 = time.perf_counter()
        time_astar = t1 - t0

        t0 = time.perf_counter()
        sma_star_path(self.graph, self.source, self.target, heuristic=self.heuristic)
        t1 = time.perf_counter()
        time_sma = t1 - t0

        return {
            "A* Recalc Time (s)": time_astar,
            "SMA* Recalc Time (s)": time_sma,
        }

    def run_all(self):
        time_data = self.compare_initial_time()
        mem_data = self.compare_memory()
        recalc_data = self.compare_recalculation()

        result = {**time_data, **mem_data, **recalc_data}
        table = [[k, f"{v:.6f}" if isinstance(v, float) else v] for k, v in result.items()]
        print(tabulate(table, headers=["Metric", "Value"], tablefmt="grid"))
        return result
