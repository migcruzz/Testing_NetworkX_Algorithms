"""
from CsvProcessor.generator import generate_random_graph
from Testers.bi_astar import AStarVsBidirectionalComparison
from Testers.d_star_lite import DStarLiteVsAStarComparison
from Testers.ida_star import IDAStarVsAStarComparison
from Testers.rtaa_star import RTAAStarVsAStarComparison
from Testers.sma_star import SMAStarVsAStarComparison

N_NODES = 100
N_EDGES = 300

DIRECTED = False

MIN_WEIGHT = 1
MAX_WEIGHT = 10000

SOURCE = 1
TARGET = 80

graph = generate_random_graph(N_NODES, N_EDGES, DIRECTED, [MIN_WEIGHT, MAX_WEIGHT])

di_graph = graph.to_directed()


df = nx.to_pandas_edgelist(graph)
print("Normal")
print(df)

di_df = nx.to_pandas_edgelist(di_graph)
print("Directed")
print(di_df)



if __name__ == "__main__":

testerBidirectional = AStarVsBidirectionalComparison(graph, SOURCE, TARGET)
testerBidirectional.run_all()

testerDstar = DStarLiteVsAStarComparison(di_graph, SOURCE, TARGET)
testerDstar.run_all()

testerSma = SMAStarVsAStarComparison(graph, SOURCE, TARGET)
testerSma.run_all()

testerIda = IDAStarVsAStarComparison(graph, SOURCE, TARGET)
testerIda.run_all()


testerBidirectional = AStarVsBidirectionalComparison(graph, SOURCE, TARGET)
testerBidirectional.run_all()

testerDstar = DStarLiteVsAStarComparison(di_graph, SOURCE, TARGET)
testerDstar.run_all()

testerRtaa = RTAAStarVsAStarComparison(graph, SOURCE, TARGET)
testerRtaa.run_all()

testerRtaa2 = RTAAStarVsAStarComparison(graph, SOURCE, TARGET, 250, 5)
testerRtaa2.run_all()

testerSma = SMAStarVsAStarComparison(graph, SOURCE, TARGET)
testerSma.run_all()

testerIda = IDAStarVsAStarComparison(graph, SOURCE, TARGET)
testerIda.run_all()

"""
from Algorithms.bi_astar import bidirectional_astar
from Graphs.graphs import draw_graph

"""
# !/usr/bin/env python3
from multiprocessing import Process, freeze_support

from CsvProcessor.generator import generate_random_graph
from Testers.bi_astar import AStarVsBidirectionalComparison
from Testers.d_star_lite import DStarLiteVsAStarComparison
from Testers.ida_star import IDAStarVsAStarComparison
from Testers.rtaa_star import RTAAStarVsAStarComparison
from Testers.sma_star import SMAStarVsAStarComparison

# Configuração
N_NODES = 100000
N_EDGES = 300000
DIRECTED = False
MIN_WEIGHT = 1
MAX_WEIGHT = 10000
SOURCE = 1
TARGET = 80000


def build_graphs():
    # gera o grafo base
    G = generate_random_graph(N_NODES, N_EDGES, DIRECTED, (MIN_WEIGHT, MAX_WEIGHT))
    # para D* Lite precisamos de um DiGraph
    DG = G.to_directed()
    return G, DG


def run_bidirectional(G):
    print("\n--- Bidirectional A* vs A* ---")
    tester = AStarVsBidirectionalComparison(G, SOURCE, TARGET)
    tester.run_all()


def run_dstar(G, DG):
    print("\n--- D* Lite vs A* ---")
    tester = DStarLiteVsAStarComparison(DG, SOURCE, TARGET)
    tester.run_all()


def run_idastar(G):
    print("\n--- IDA* vs A* ---")
    tester = IDAStarVsAStarComparison(G, SOURCE, TARGET)
    tester.run_all()


def run_rtaa(G):
    print("\n--- RTAA* vs A* (lookahead=5, move_limit=1) ---")
    tester = RTAAStarVsAStarComparison(G, SOURCE, TARGET, lookahead=5, move_limit=1)
    tester.run_all()


def run_sma(G):
    print("\n--- SMA* vs A* ---")
    tester = SMAStarVsAStarComparison(G, SOURCE, TARGET)
    tester.run_all()


if __name__ == "__main__":
    # Necessário no Windows para multiprocessing com tracemalloc, etc.
    freeze_support()

    # Constroi grafos
    G, DG = build_graphs()

    # Cria e inicia processos
    procs = [
        Process(target=run_bidirectional, args=(G,)),
        Process(target=run_dstar, args=(G, DG)),
        Process(target=run_idastar, args=(G,)),
        Process(target=run_rtaa, args=(G,)),
        Process(target=run_sma, args=(G,)),
    ]
    for p in procs:
        p.start()

    # Aguarda todos terminarem
    for p in procs:
        p.join()
"""

"""
Run every comparison in a separate process, but all of them receive the
*same* base graph so the test is fair.
"""
# !/usr/bin/env python3
import re
from multiprocessing import Process, Manager, freeze_support
from pathlib import Path

import networkx as nx
import pandas as pd
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter

from Algorithms.ida_star import idastar_path
from Algorithms.rtaa_star import rtaa_star_path
from Algorithms.sma_star import sma_star_path
from CsvProcessor.generator import generate_graph_from_csv
from Testers.bi_astar import AStarVsBidirectionalComparison
from Testers.d_star_lite import DStarLiteVsAStarComparison
from Testers.ida_star import IDAStarVsAStarComparison
from Testers.rtaa_star import RTAAStarVsAStarComparison
from Testers.sma_star import SMAStarVsAStarComparison

from Config import MEMORY_LIMIT, LOOKAHEAD, MOVELIMIT, N_MODIFICATIONS, SOURCE, TARGET, CSV_PATH, EXCEL_FILE


# ─── Global settings ──────────────────────────────────────────────────────────
DIRECTED = False


# ─── Excel helpers ────────────────────────────────────────────────────────────
def sanitize_sheet_name(name: str) -> str:
    return re.sub(r'[:\\/?*\[\]]', "", name)[:31]


def append_sheet(result_dict, sheet_name, excel_path=EXCEL_FILE):
    df = pd.DataFrame(result_dict.items(), columns=["Metric", "Value"])
    sheet_name = sanitize_sheet_name(sheet_name)
    mode = "a" if Path(excel_path).exists() else "w"

    with pd.ExcelWriter(
            excel_path,
            engine="openpyxl",
            mode=mode,
            if_sheet_exists=None if mode == "w" else "replace",
    ) as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
        ws = writer.sheets[sheet_name]

        bold = Font(bold=True)
        centre = Alignment(horizontal="center")

        # header
        for cell in ws[1]:
            cell.font = bold
            cell.alignment = centre

        # values
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
            for cell in row:
                cell.alignment = centre

        # autosize columns
        for col_idx in range(1, ws.max_column + 1):
            col_letter = get_column_letter(col_idx)
            max_len = max(
                len(str(c.value)) if c.value is not None else 0
                for c in ws[col_letter]
            )
            ws.column_dimensions[col_letter].width = max_len + 2


# ─── Worker wrappers ──────────────────────────────────────────────────────────
def run_bidirectional(graph, n_mods, shared):
    tester = AStarVsBidirectionalComparison(graph, SOURCE, TARGET, n_mods)
    shared["Bidirectional A*"] = tester.run_all()

    try:
        _, full_path, _ = bidirectional_astar(graph, SOURCE, TARGET)
        draw_graph(
            graph,
            SOURCE,
            TARGET,
            full_path,
            "Graphs/Plots/path_bidirectional_astar.png",
        )
    except nx.NetworkXNoPath:
        pass


def run_dstar(di_graph, n_mods, shared):
    tester = DStarLiteVsAStarComparison(di_graph, SOURCE, TARGET, n_mods)
    shared["D* Lite"] = tester.run_all()
    try:
        path = nx.astar_path(di_graph, SOURCE, TARGET, weight="weight")
        draw_graph(di_graph, SOURCE, TARGET, path, "Graphs/Plots/path_dstar_lite.png")
    except nx.NetworkXNoPath:
        pass


def run_idastar(graph, n_mods, shared):
    tester = IDAStarVsAStarComparison(graph, SOURCE, TARGET, n_mods)
    shared["IDA*"] = tester.run_all()
    try:
        path = idastar_path(graph, SOURCE, TARGET)
        draw_graph(graph, SOURCE, TARGET, path, "Graphs/Plots/path_idastar.png")
    except Exception:
        pass


def run_rtaa(graph, lookahead, move_limit, n_mods, shared):
    tester = RTAAStarVsAStarComparison(graph, SOURCE, TARGET, lookahead, move_limit, n_mods)
    key = f"RTAA* (L={lookahead}, M={move_limit})"
    shared[key] = tester.run_all()
    try:
        path = rtaa_star_path(graph, SOURCE, TARGET, lookahead=lookahead, move_limit=move_limit)
        draw_graph(graph, SOURCE, TARGET, path, "Graphs/Plots/path_rtaa_star.png")
    except Exception:
        pass


def run_sma(graph, memory_limit, n_mods, shared):
    tester = SMAStarVsAStarComparison(
        graph, SOURCE, TARGET, heuristic=None, n_modifications=n_mods, memory_limit=memory_limit
    )
    shared["SMA*"] = tester.run_all()
    try:
        path = sma_star_path(graph, SOURCE, TARGET, memory_limit=memory_limit)
        draw_graph(graph, SOURCE, TARGET, path, "Graphs/Plots/path_sma_star.png")
    except Exception:
        pass


def launch(worker, *args):
    worker(*args)


# ─── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    freeze_support()

    base_graph = generate_graph_from_csv(CSV_PATH, "distance_km", DIRECTED)
    if not nx.has_path(base_graph, SOURCE, TARGET):
        print("No path between source and target. Aborting.")
        exit(1)

    initial_path = nx.shortest_path(base_graph, SOURCE, TARGET, weight="weight")
    draw_graph(base_graph, SOURCE, TARGET, initial_path,
               f"Graphs/Plots/graph_{SOURCE}_to_{TARGET}.png")

    directed_graph = base_graph.to_directed()

    manager = Manager()
    shared_results = manager.dict()

    processes = [
        Process(target=launch, args=(run_bidirectional,
                                     base_graph, N_MODIFICATIONS, shared_results)),
        Process(target=launch, args=(run_dstar,
                                     directed_graph, N_MODIFICATIONS, shared_results)),
        Process(target=launch, args=(run_idastar,
                                     base_graph, N_MODIFICATIONS, shared_results)),
        Process(target=launch, args=(run_rtaa,
                                     base_graph, LOOKAHEAD, MOVELIMIT,
                                     N_MODIFICATIONS, shared_results)),
        Process(target=launch, args=(run_sma,
                                     base_graph, MEMORY_LIMIT,
                                     N_MODIFICATIONS, shared_results)),
    ]

    for p in processes:
        p.start()
    for p in processes:
        p.join()

    for algorithm, metrics in shared_results.items():
        append_sheet(metrics, algorithm, EXCEL_FILE)

    print(f"All metrics written to {EXCEL_FILE}")
