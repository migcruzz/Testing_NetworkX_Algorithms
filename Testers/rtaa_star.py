import random
import statistics
import time
import tracemalloc

import networkx as nx
from networkx.algorithms.shortest_paths.astar import astar_path
from tabulate import tabulate

from Algorithms.rtaa_star import rtaa_star_path


class RTAAStarVsAStarComparison:
    def __init__(self, graph: nx.Graph, source, target, lookahead=5, move_limit=1, n_modifications=50):
        self.graph = graph
        self.source = source
        self.target = target
        self.lookahead = lookahead
        self.move_limit = move_limit
        self.name = "RTAA*"
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
        path_rtaa = rtaa_star_path(self.graph, self.source, self.target,
                                   lookahead=self.lookahead, move_limit=self.move_limit)
        t1 = time.perf_counter()
        time_rtaa = t1 - t0
        cost_rtaa = self.compute_cost(path_rtaa)

        return {
            "A* Time (s)": time_astar,
            "RTAA* Time (s)": time_rtaa,
            "A* Cost": cost_astar,
            "RTAA* Cost": cost_rtaa,
        }

    def compare_memory(self, runs: int = 5):
        peaks_astar = []
        peaks_rtaa = []

        for _ in range(runs):
            tracemalloc.start()
            astar_path(self.graph, self.source, self.target, weight="weight")
            _, peak_a = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            peaks_astar.append(peak_a)

            tracemalloc.start()
            rtaa_star_path(
                self.graph,
                self.source,
                self.target,
                lookahead=self.lookahead,
                move_limit=self.move_limit,
            )
            _, peak_r = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            peaks_rtaa.append(peak_r)

        mib = 1024 * 1024
        return {
            "A* Peak Memory (MiB)": max(peaks_astar) / mib,
            "A* Avg Memory (MiB)": statistics.mean(peaks_astar) / mib,
            "RTAA* Peak Memory (MiB)": max(peaks_rtaa) / mib,
            "RTAA* Avg Memory (MiB)": statistics.mean(peaks_rtaa) / mib,
        }

    def compare_recalculation(self):
        neighbor = next(iter(self.graph[self.source]))
        self.graph[self.source][neighbor]["weight"] += 3

        t0 = time.perf_counter()
        astar_path(self.graph, self.source, self.target, weight="weight")
        t1 = time.perf_counter()
        time_astar = t1 - t0

        t0 = time.perf_counter()
        rtaa_star_path(self.graph, self.source, self.target,
                       lookahead=self.lookahead, move_limit=self.move_limit)
        t1 = time.perf_counter()
        time_rtaa = t1 - t0

        return {
            "A* Recalc Time (s)": time_astar,
            "RTAA* Recalc Time (s)": time_rtaa,
        }

    def compare_bulk_modifications(self):
        all_edges = list(self.graph.edges)
        times_astar = []
        times_rtaa = []

        for _ in range(self.n_modifications):
            u, v = random.choice(all_edges)
            new_w = random.randint(5, 50)
            self.graph[u][v]["weight"] = new_w

            t0 = time.perf_counter()
            rtaa_star_path(self.graph, self.source, self.target,
                           lookahead=self.lookahead, move_limit=self.move_limit)
            t1 = time.perf_counter()
            times_rtaa.append(t1 - t0)

            t0 = time.perf_counter()
            astar_path(self.graph, self.source, self.target, weight="weight")
            t1 = time.perf_counter()
            times_astar.append(t1 - t0)

        return {
            "RTAA* Bulk Avg Time (s)": statistics.mean(times_rtaa),
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
