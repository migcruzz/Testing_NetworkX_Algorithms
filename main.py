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

from CsvProcessor.generator import generate_random_graph
from Testers.bi_astar import AStarVsBidirectionalComparison
from Testers.d_star_lite import DStarLiteVsAStarComparison
from Testers.ida_star import IDAStarVsAStarComparison
from Testers.rtaa_star import RTAAStarVsAStarComparison
from Testers.sma_star import SMAStarVsAStarComparison

# ─── Configuration ─────────────────────────────────────────────────────────────
N_NODES    = 10000
N_EDGES    = 3000000
DIRECTED   = False
MIN_WEIGHT = 1
MAX_WEIGHT = 100000
SOURCE     = 1
TARGET     = 90

# ─── Worker wrappers ───────────────────────────────────────────────────────────
def run_bidirectional(G: nx.Graph):
    tester = AStarVsBidirectionalComparison(G, SOURCE, TARGET)
    print("\n--- Bidirectional A* vs A* ---")
    tester.run_all()

def run_dstar(DG: nx.DiGraph):
    tester = DStarLiteVsAStarComparison(DG, SOURCE, TARGET)
    print("\n--- D* Lite vs A* ---")
    tester.run_all()

def run_idastar(G: nx.Graph):
    tester = IDAStarVsAStarComparison(G, SOURCE, TARGET)
    print("\n--- IDA* vs A* ---")
    tester.run_all()

def run_rtaa(G: nx.Graph):
    tester = RTAAStarVsAStarComparison(G, SOURCE, TARGET, lookahead=100, move_limit=1)
    print("\n--- RTAA* vs A* ---")
    tester.run_all()

def run_sma(G: nx.Graph):
    tester = SMAStarVsAStarComparison(G, SOURCE, TARGET)
    print("\n--- SMA* vs A* ---")
    tester.run_all()

# ─── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    freeze_support()  # needed on Windows

    # 1. Build a single base graph (and its directed copy) to share with every test
    base_graph = generate_random_graph(
        N_NODES, N_EDGES, DIRECTED, (MIN_WEIGHT, MAX_WEIGHT)
    )
    directed_graph = base_graph.to_directed()

    # 2. Launch each comparison in its own process,
    #    passing the same graph (it will be pickled & copied for the child)
    processes = [
        Process(target=run_bidirectional, args=(base_graph,)),
        Process(target=run_dstar,        args=(directed_graph,)),
        Process(target=run_idastar,      args=(base_graph,)),
        Process(target=run_rtaa,         args=(base_graph,)),
        Process(target=run_sma,          args=(base_graph,)),
    ]

    for p in processes:
        p.start()
    for p in processes:
        p.join()
