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
from Algorithms.bi_astar import bidirectional_astar
from CsvProcessor.generator import generate_graph_from_csv
from Testers.bi_astar import AStarVsBidirectionalComparison
from Testers.d_star_lite import DStarLiteVsAStarComparison
from Testers.ida_star import IDAStarVsAStarComparison
from Testers.rtaa_star import RTAAStarVsAStarComparison
from Testers.sma_star import SMAStarVsAStarComparison
from Graphs.graphs import draw_graph

from Config import MEMORY_LIMIT, LOOKAHEAD, MOVELIMIT, N_MODIFICATIONS, SOURCE, TARGET, CSV_PATH, EXCEL_FILE, DIRECTED

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

        for cell in ws[1]:
            cell.font = bold
            cell.alignment = centre

        for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
            for cell in row:
                cell.alignment = centre

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
        draw_graph(graph, SOURCE, TARGET, path=full_path, metrics=shared["Bidirectional A*"], output_path="Graphs/Plots/path_bidirectional_astar.png")
    except nx.NetworkXNoPath:
        pass

def run_dstar(di_graph, n_mods, shared):
    tester = DStarLiteVsAStarComparison(di_graph, SOURCE, TARGET, n_mods)
    shared["D* Lite"] = tester.run_all()
    try:
        path = nx.astar_path(di_graph, SOURCE, TARGET, weight="weight")
        draw_graph(di_graph, SOURCE, TARGET, path=path, metrics=shared["D* Lite"], output_path="Graphs/Plots/path_dstar_lite.png")
    except nx.NetworkXNoPath:
        pass

def run_idastar(graph, n_mods, shared):
    tester = IDAStarVsAStarComparison(graph, SOURCE, TARGET, n_mods)
    shared["IDA*"] = tester.run_all()
    try:
        path = idastar_path(graph, SOURCE, TARGET)
        draw_graph(graph, SOURCE, TARGET, path=path, metrics=shared["IDA*"], output_path="Graphs/Plots/path_idastar.png")
    except Exception:
        pass

def run_rtaa(graph, lookahead, move_limit, n_mods, shared):
    tester = RTAAStarVsAStarComparison(graph, SOURCE, TARGET, lookahead, move_limit, n_mods)
    key = f"RTAA* (L={lookahead}, M={move_limit})"
    shared[key] = tester.run_all()
    try:
        path = rtaa_star_path(graph, SOURCE, TARGET, lookahead=lookahead, move_limit=move_limit)
        draw_graph(graph, SOURCE, TARGET, path=path, metrics=shared[key], output_path="Graphs/Plots/path_rtaa_star.png")
    except Exception:
        pass

def run_sma(graph, memory_limit, n_mods, shared):
    tester = SMAStarVsAStarComparison(graph, SOURCE, TARGET, heuristic=None, n_modifications=n_mods, memory_limit=memory_limit)
    shared["SMA*"] = tester.run_all()
    try:
        path = sma_star_path(graph, SOURCE, TARGET, memory_limit=memory_limit)
        draw_graph(graph, SOURCE, TARGET, path=path, metrics=shared["SMA*"], output_path="Graphs/Plots/path_sma_star.png")
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
    draw_graph(base_graph, SOURCE, TARGET, path=initial_path, output_path=f"Graphs/Plots/graph_{SOURCE}_to_{TARGET}.png")

    directed_graph = base_graph.to_directed()
    manager = Manager()
    shared_results = manager.dict()

    processes = [
        Process(target=launch, args=(run_bidirectional, base_graph, N_MODIFICATIONS, shared_results)),
        Process(target=launch, args=(run_dstar, directed_graph, N_MODIFICATIONS, shared_results)),
        Process(target=launch, args=(run_idastar, base_graph, N_MODIFICATIONS, shared_results)),
        Process(target=launch, args=(run_rtaa, base_graph, LOOKAHEAD, MOVELIMIT, N_MODIFICATIONS, shared_results)),
        Process(target=launch, args=(run_sma, base_graph, MEMORY_LIMIT, N_MODIFICATIONS, shared_results)),
    ]

    for p in processes:
        p.start()
    for p in processes:
        p.join()

    for algorithm, metrics in shared_results.items():
        append_sheet(metrics, algorithm, EXCEL_FILE)

    print(f"All metrics written to {EXCEL_FILE}")