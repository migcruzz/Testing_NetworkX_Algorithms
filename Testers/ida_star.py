import statistics
import time
import tracemalloc

import networkx as nx
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

    def compare_memory(self, runs: int = 5):

        peaks_astar = []
        peaks_ida = []

        for _ in range(runs):
            # A*
            tracemalloc.start()
            nx.astar_path(self.graph, self.source, self.target, weight="weight")
            _, peak_astar = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            peaks_astar.append(peak_astar)

            # IDA*
            tracemalloc.start()
            idastar_path(self.graph, self.source, self.target)
            _, peak_ida = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            peaks_ida.append(peak_ida)

        mib = 1024 * 1024
        return {
            "A* Peak Memory (MiB)": max(peaks_astar) / mib,
            "A* Avg Memory (MiB)": statistics.mean(peaks_astar) / mib,
            "IDA* Peak Memory (MiB)": max(peaks_ida) / mib,
            "IDA* Avg Memory (MiB)": statistics.mean(peaks_ida) / mib,
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
