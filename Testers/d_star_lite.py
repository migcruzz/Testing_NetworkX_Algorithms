import random
import statistics
import time
import tracemalloc

import networkx as nx
from tabulate import tabulate

from Algorithms.d_star_lite import (
    new_dstar_lite_instance,
    d_star_modify_edge,
    d_star_recalculate_path,
)


class DStarLiteVsAStarComparison:
    def __init__(self, graph: nx.DiGraph, source, target):
        self.graph = graph
        self.source = source
        self.target = target

    def compare_initial_time(self):
        t0 = time.perf_counter()
        dstar = new_dstar_lite_instance(self.graph, self.source, self.target)
        path_d = dstar.get_path()
        t1 = time.perf_counter()
        time_dstar = t1 - t0
        cost_d = dstar.get_path_cost()

        t0 = time.perf_counter()
        path_a = nx.astar_path(self.graph, self.source, self.target, weight="weight")
        t1 = time.perf_counter()
        time_astar = t1 - t0
        cost_a = sum(
            self.graph[path_a[i]][path_a[i + 1]]["weight"] for i in range(len(path_a) - 1)
        )

        return {

            "A* Time (s)": time_astar,
            "D* Lite Time (s)": time_dstar,
            "A* Cost": cost_a,
            "D* Lite Cost": cost_d
        }

    def compare_memory(self, runs: int = 5):

        peaks_astar = []
        peaks_dstar = []

        for _ in range(runs):
            # A*
            tracemalloc.start()
            nx.astar_path(self.graph, self.source, self.target, weight="weight")
            _, peak_astar = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            peaks_astar.append(peak_astar)

            # D* Lite
            tracemalloc.start()
            new_dstar_lite_instance(self.graph, self.source, self.target)
            _, peak_dstar = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            peaks_dstar.append(peak_dstar)

        mib = 1024 * 1024
        return {
            "A* Peak Memory (MiB)": max(peaks_astar) / mib,
            "A* Avg Memory (MiB)": statistics.mean(peaks_astar) / mib,
            "D* Lite Peak Memory (MiB)": max(peaks_dstar) / mib,
            "D* Lite Avg Memory (MiB)": statistics.mean(peaks_dstar) / mib,
        }

    def compare_recalculation(self):
        dstar = new_dstar_lite_instance(self.graph, self.source, self.target)
        path = dstar.get_path()
        if not path or len(path) < 3:
            raise ValueError("Insufficient path for modification")

        edges_to_modify = random.sample(list(zip(path, path[1:])), k=min(10, len(path) - 1))

        total_time_dstar = 0.0
        total_time_astar = 0.0

        for u, v in edges_to_modify:
            new_w = random.randint(5, 50)

            # D* Lite incremental update
            t0 = time.perf_counter()
            d_star_modify_edge(dstar, u, v, new_w)
            d_star_recalculate_path(dstar)
            t1 = time.perf_counter()
            total_time_dstar += t1 - t0

            # A* recomputation
            self.graph[u][v]["weight"] = new_w
            t0 = time.perf_counter()
            _ = nx.astar_path_length(self.graph, self.source, self.target, weight="weight")
            t1 = time.perf_counter()
            total_time_astar += t1 - t0

        return {
            "A* Recalc Total (s)": total_time_astar,
            "D* Lite Recalc Total (s)": total_time_dstar
        }

    def run_all(self):
        time_data = self.compare_initial_time()
        mem_data = self.compare_memory()
        recalc_data = self.compare_recalculation()

        result = {**time_data, **mem_data, **recalc_data}
        table = [[k, f"{v:.6f}" if isinstance(v, float) else v] for k, v in result.items()]
        print(tabulate(table, headers=["Metric", "Value"], tablefmt="grid"))
        return result
