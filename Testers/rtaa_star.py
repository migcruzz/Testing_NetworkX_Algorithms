import time

import networkx as nx
from memory_profiler import memory_usage
from networkx.algorithms.shortest_paths.astar import astar_path
from tabulate import tabulate

from Algorithms.rtaa_star import rtaa_star_path


class RTAAStarVsAStarComparison:
    def __init__(self, graph: nx.Graph, source, target, lookahead=5, move_limit=1):
        self.graph = graph
        self.source = source
        self.target = target
        self.lookahead = lookahead
        self.move_limit = move_limit

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

    def compare_memory(self):
        def run_astar():
            astar_path(self.graph, self.source, self.target, weight="weight")

        def run_rtaa():
            rtaa_star_path(self.graph, self.source, self.target,
                           lookahead=self.lookahead, move_limit=self.move_limit)

        mem_astar = max(memory_usage(run_astar, max_iterations=1))
        mem_rtaa = max(memory_usage(run_rtaa, max_iterations=1))

        return {
            "A* Memory (MiB)": mem_astar,
            "RTAA* Memory (MiB)": mem_rtaa,
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

    def run_all(self):
        time_data = self.compare_initial_time()
        mem_data = self.compare_memory()
        recalc_data = self.compare_recalculation()

        result = {**time_data, **mem_data, **recalc_data}
        table = [[k, f"{v:.6f}" if isinstance(v, float) else v] for k, v in result.items()]
        print(tabulate(table, headers=["Metric", "Value"], tablefmt="grid"))
        return result
