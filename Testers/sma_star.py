import random
import statistics
import time
import tracemalloc

import networkx as nx
from networkx.algorithms.shortest_paths.astar import astar_path
from tabulate import tabulate

from Algorithms.sma_star import sma_star_path
from Config import MEMORY_LIMIT



class SMAStarVsAStarComparison:
    def __init__(self, graph: nx.Graph, source, target, heuristic=None, memory_limit=MEMORY_LIMIT, n_modifications=50):
        self.graph = graph
        self.source = source
        self.target = target
        self.heuristic = heuristic
        self.memory_limit = memory_limit
        self.name = "SMA*"
        self.n_modifications = n_modifications

    def compute_cost(self, path):
        return sum(self.graph[path[i]][path[i + 1]]["weight"] for i in range(len(path) - 1))

    def compare_initial_time(self):
        t0 = time.perf_counter()
        path_astar = astar_path(self.graph, self.source, self.target, weight="weight")
        t1 = time.perf_counter()
        time_astar = t1 - t0
        cost_astar = self.compute_cost(path_astar)

        t0 = time.perf_counter()
        path_sma = sma_star_path(
            self.graph, self.source, self.target,
            heuristic=self.heuristic,
            memory_limit=self.memory_limit
        )
        t1 = time.perf_counter()
        time_sma = t1 - t0
        cost_sma = self.compute_cost(path_sma)

        return {
            "A* Time (s)": time_astar,
            "SMA* Time (s)": time_sma,
            "A* Cost": cost_astar,
            "SMA* Cost": cost_sma,
        }

    def compare_memory(self, runs: int = 5):
        peaks_astar = []
        peaks_sma = []
        mib = 1024 * 1024

        for _ in range(runs):
            tracemalloc.start()
            nx.astar_path(self.graph, self.source, self.target, weight="weight")
            _, peak_a = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            peaks_astar.append(peak_a / mib)

            tracemalloc.start()
            sma_star_path(
                self.graph, self.source, self.target,
                heuristic=self.heuristic,
                memory_limit=self.memory_limit
            )
            _, peak_s = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            peaks_sma.append(peak_s / mib)

        return {
            "A* Peak Memory (MiB)": max(peaks_astar),
            "A* Avg Memory (MiB)": statistics.mean(peaks_astar),
            "SMA* Peak Memory (MiB)": max(peaks_sma),
            "SMA* Avg Memory (MiB)": statistics.mean(peaks_sma),
        }

    def compare_recalculation(self):
        neighbor = next(iter(self.graph[self.source]))
        self.graph[self.source][neighbor]["weight"] += 5

        t0 = time.perf_counter()
        astar_path(self.graph, self.source, self.target, weight="weight")
        t1 = time.perf_counter()
        time_astar = t1 - t0

        t0 = time.perf_counter()
        sma_star_path(
            self.graph, self.source, self.target,
            heuristic=self.heuristic,
            memory_limit=self.memory_limit
        )
        t1 = time.perf_counter()
        time_sma = t1 - t0

        return {
            "A* Recalc Time (s)": time_astar,
            "SMA* Recalc Time (s)": time_sma,
        }

    def compare_bulk_modifications(self):
        all_edges = list(self.graph.edges)
        times_astar = []
        times_sma = []

        for _ in range(self.n_modifications):
            u, v = random.choice(all_edges)
            new_w = random.randint(5, 50)
            self.graph[u][v]["weight"] = new_w

            t0 = time.perf_counter()
            sma_star_path(self.graph, self.source, self.target, heuristic=self.heuristic)
            t1 = time.perf_counter()
            times_sma.append(t1 - t0)

            t0 = time.perf_counter()
            astar_path(self.graph, self.source, self.target, weight="weight")
            t1 = time.perf_counter()
            times_astar.append(t1 - t0)

        return {
            "SMA* Bulk Avg Time (s)": statistics.mean(times_sma),
            "A* Bulk Avg Time (s)": statistics.mean(times_astar),
            "Bulk Modifications Count": self.n_modifications
        }

    def run_all(self):
        time_data = self.compare_initial_time()
        mem_data = self.compare_memory()
        recalc_data = self.compare_recalculation()
        bulk_data = self.compare_bulk_modifications()

        result = {**time_data, **mem_data, **recalc_data, **bulk_data}
        table = [[k, f"{v:.6f}" if isinstance(v, float) else v] for k, v in result.items()]
        print(tabulate(table, headers=["Metric", "Value"], tablefmt="grid"))
        return result
