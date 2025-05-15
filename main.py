from multiprocessing import Process, freeze_support
import networkx as nx

from Algorithms.ida_star import idastar_path
from Algorithms.rtaa_star import rtaa_star_path
from Algorithms.sma_star import sma_star_path
from Graphs.graphs import draw_graph
from CsvProcessor.generator import generate_graph_from_csv
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
            Process(target=run_sma, args=(base_graph, MAX_NODES_IN_MEMORY)),
            Process(target=run_bidirectional, args=(base_graph,)),
            Process(target=run_dstar, args=(directed_graph,)),
            Process(target=run_idastar, args=(base_graph,)),
            Process(target=run_rtaa, args=(base_graph,)),
        ]

        for p in processes:
            p.start()
        for p in processes:
            p.join()

