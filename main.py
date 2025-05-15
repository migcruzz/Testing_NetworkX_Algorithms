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
from multiprocessing import Process, freeze_support
import networkx as nx

from Algorithms.ida_star import idastar_path
from Algorithms.rtaa_star import rtaa_star_path
from Algorithms.sma_star import sma_star_path
from Graphs.graphs import draw_graph
from CsvProcessor.generator import generate_graph_from_csv

import re
from multiprocessing import Process, freeze_support, Manager
from pathlib import Path

import pandas as pd
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter


from Testers.bi_astar import AStarVsBidirectionalComparison
from Testers.d_star_lite import DStarLiteVsAStarComparison
from Testers.ida_star import IDAStarVsAStarComparison
from Testers.rtaa_star import RTAAStarVsAStarComparison
from Testers.sma_star import SMAStarVsAStarComparison

# ─── Configuration ─────────────────────────────────────────────────────────────
DIRECTED = False
SOURCE = "Luxembourg"
TARGET = "Barcelona"
MAX_NODES_IN_MEMORY = 40
# Configuração
N_NODES = 1000
N_EDGES = 3000
N_MODIFICATIONS = 10
# N_MODIFICATIONS = round(N_EDGES * 0.5)

LOOKAHEAD = 25
MOVELIMIT = 3

DIRECTED = False
MIN_WEIGHT = 1
MAX_WEIGHT = 300
SOURCE = 1
TARGET = 900
# ─── Worker wrappers ───────────────────────────────────────────────────────────
def run_bidirectional(G: nx.Graph):
    tester = AStarVsBidirectionalComparison(G, SOURCE, TARGET)
    print("\n--- Bidirectional A* vs A* ---")
    tester.run_all()

    try:
        path = nx.bidirectional_shortest_path(G, SOURCE, TARGET)
        draw_graph(G, source=SOURCE, target=TARGET, path=path, output_path="Graphs/path_bidirectional_astar.png")
    except nx.NetworkXNoPath:
        print("No path found for Bidirectional A*")

def run_dstar(DG: nx.DiGraph):
    tester = DStarLiteVsAStarComparison(DG, SOURCE, TARGET)
    print("\n--- D* Lite vs A* ---")
    tester.run_all()

    # Se tiveres função para recuperar o caminho, substitui esta parte:
    try:
        path = nx.astar_path(DG, SOURCE, TARGET, weight="weight")  # Placeholder
        draw_graph(DG, source=SOURCE, target=TARGET, path=path, output_path="Graphs/path_dstar_lite.png")
    except nx.NetworkXNoPath:
        print("No path found for D* Lite")

def run_idastar(G: nx.Graph):
    tester = IDAStarVsAStarComparison(G, SOURCE, TARGET)
    print("\n--- IDA* vs A* ---")
    tester.run_all()

    try:
        path = idastar_path(G, SOURCE, TARGET)
        draw_graph(G, source=SOURCE, target=TARGET, path=path, output_path="Graphs/path_idastar.png")
    except Exception as e:
        print(f"IDA* path error: {e}")

def run_rtaa(G: nx.Graph):
    tester = RTAAStarVsAStarComparison(G, SOURCE, TARGET, lookahead=100, move_limit=1)
    print("\n--- RTAA* vs A* ---")
    tester.run_all()

    try:
        path = rtaa_star_path(G, SOURCE, TARGET, lookahead=100, move_limit=1)
        draw_graph(G, source=SOURCE, target=TARGET, path=path, output_path="Graphs/path_rtaa_star.png")
    except Exception as e:
        print(f"RTAA* path error: {e}")

def run_sma(G: nx.Graph, memory_limit: int):
    tester = SMAStarVsAStarComparison(G, SOURCE, TARGET, memory_limit=memory_limit)
    print(f"\n--- SMA* vs A* (Memory limit: {memory_limit}) ---")
    tester.run_all()

    try:
        path = sma_star_path(G, SOURCE, TARGET, memory_limit=memory_limit)
        draw_graph(G, source=SOURCE, target=TARGET, path=path, output_path="Graphs/path_sma_star.png")
    except Exception as e:
        print(f"SMA* path error: {e}")


def sanitize_sheet_name(name):
    return re.sub(r'[:\\/?*\[\]]', '', name)[:31]


def append_sheet(result_dict, sheet_name, caminho_excel="metrics.xlsx"):
    df = pd.DataFrame(result_dict.items(), columns=["Métrica", "Valor"])
    sheet_name = sanitize_sheet_name(sheet_name)

    if Path(caminho_excel).exists():
        mode = "a"
        if_sheet_exists = "replace"
    else:
        mode = "w"
        if_sheet_exists = None

    with pd.ExcelWriter(
            caminho_excel,
            engine="openpyxl",
            mode=mode,
            if_sheet_exists=if_sheet_exists,
    ) as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)

        worksheet = writer.sheets[sheet_name]

        header_font = Font(bold=True)
        center_align = Alignment(horizontal="center")

        for col_idx, column_cells in enumerate(worksheet.iter_cols(min_row=1, max_row=1), start=1):
            for cell in column_cells:
                cell.font = header_font
                cell.alignment = center_align

        for col_idx, column_cells in enumerate(worksheet.iter_cols(min_row=1, max_row=worksheet.max_row), start=1):
            max_length = max(len(str(cell.value)) if cell.value is not None else 0 for cell in column_cells)
            adjusted_width = max_length + 2
            col_letter = get_column_letter(col_idx)
            worksheet.column_dimensions[col_letter].width = adjusted_width

        for row in worksheet.iter_rows(min_row=2, max_row=worksheet.max_row):
            for cell in row:
                cell.alignment = center_align


def run_tester(tester_class, graph, alg_name, shared_results, *args):
    tester = tester_class(graph, SOURCE, TARGET, *args)
    print(f"\n--- {alg_name} ---")
    result = tester.run_all()
    shared_results[alg_name] = result


# ─── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    freeze_support()

    base_graph = generate_graph_from_csv("Csv/cities_nodes_special.csv", weight_field="distance_km", directed=DIRECTED)
    directed_graph = base_graph.to_directed()
    if not nx.has_path(base_graph, SOURCE, TARGET):
        print(f"No path found between {SOURCE} and {TARGET}. Aborting.")
    else:
        print(f"Path found between {SOURCE} and {TARGET}.")

        # Guardar visualização do grafo com o caminho
        path = nx.shortest_path(base_graph, source=SOURCE, target=TARGET, weight="weight")
        output_path = f"Graphs/graph_{SOURCE}_to_{TARGET}.png"
        draw_graph(base_graph, source=SOURCE, target=TARGET, path=path, output_path=output_path)
        print(f"Grafo guardado como imagem em: {output_path}")

        # Iniciar testes
        print("Running tests...")

        processes = [
            Process(
                target=run_tester,
                args=(
                    AStarVsBidirectionalComparison,
                    base_graph,
                    "Bidirectional A*",
                    shared_results,
                    N_MODIFICATIONS,
                ),
            ),

            Process(
                target=run_tester,
                args=(
                    DStarLiteVsAStarComparison,
                    directed_graph,
                    "D* Lite",
                    shared_results,
                    N_MODIFICATIONS,
                ),
            ),

            Process(
                target=run_tester,
                args=(
                    IDAStarVsAStarComparison,
                    base_graph,
                    "IDA*",
                    shared_results,
                    N_MODIFICATIONS,
                ),
            ),

            Process(
                target=run_tester,
                args=(
                    RTAAStarVsAStarComparison,
                    base_graph,
                    f"RTAA* (lookahead={LOOKAHEAD}, move_limit={MOVELIMIT})",
                    shared_results,
                    LOOKAHEAD,
                    MOVELIMIT,
                    N_MODIFICATIONS,
                ),
            ),

            Process(
                target=run_tester,
                args=(
                    SMAStarVsAStarComparison,
                    base_graph,
                    "SMA*",
                    shared_results,
                    None,
                    N_MODIFICATIONS,
                ),
            ),
        ]

    for p in processes:
        p.start()
    for p in processes:
        p.join()
