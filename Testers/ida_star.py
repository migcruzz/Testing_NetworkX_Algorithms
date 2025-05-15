import time

import networkx as nx
from memory_profiler import memory_usage
from tabulate import tabulate

from Algorithms.ida_star import idastar_path


class IDAStarVsAStarComparison:
    def __init__(self, graph: nx.Graph, source, target):
        self.graph = graph
        self.source = source
        self.target = target

    def compute_cost(self, path):
        return sum(self.graph[path[i]][path[i + 1]]["weight"] for i in range(len(path) - 1))

    def compare_initial_time(self):
        t0 = time.perf_counter()
        path_ida = idastar_path(self.graph, self.source, self.target)
        t1 = time.perf_counter()
        time_ida = t1 - t0
        cost_ida = self.compute_cost(path_ida)

        t0 = time.perf_counter()
        path_astar = nx.astar_path(self.graph, self.source, self.target, weight="weight")
        t1 = time.perf_counter()
        time_astar = t1 - t0
        cost_astar = self.compute_cost(path_astar)

        return {
            "A* Time (s)": time_astar,
            "IDA* Time (s)": time_ida,
            "A* Cost": cost_astar,
            "IDA* Cost": cost_ida
        }

    def compare_memory(self):
        def run_ida():
            idastar_path(self.graph, self.source, self.target)

        def run_astar():
            nx.astar_path(self.graph, self.source, self.target, weight="weight")

        mem_ida = max(memory_usage(run_ida, max_iterations=1))
        mem_astar = max(memory_usage(run_astar, max_iterations=1))

        return {
            "A* Memory (MiB)": mem_astar,
            "IDA* Memory (MiB)": mem_ida
        }

    def compare_recalculation(self):
        neighbor = next(iter(self.graph[self.source]))
        self.graph[self.source][neighbor]["weight"] += 2

        t0 = time.perf_counter()
        idastar_path(self.graph, self.source, self.target)
        t1 = time.perf_counter()
        time_ida = t1 - t0

        t0 = time.perf_counter()
        nx.astar_path(self.graph, self.source, self.target, weight="weight")
        t1 = time.perf_counter()
        time_astar = t1 - t0

        return {
            "A* Recalc Time (s)": time_astar,
            "IDA* Recalc Time (s)": time_ida
        }

    def run_all(self):
        time_data = self.compare_initial_time()
        mem_data = self.compare_memory()
        recalc_data = self.compare_recalculation()

        result = {**time_data, **mem_data, **recalc_data}
        table = [[k, f"{v:.6f}" if isinstance(v, float) else v] for k, v in result.items()]
        print(tabulate(table, headers=["Metric", "Value"], tablefmt="grid"))
        return result
