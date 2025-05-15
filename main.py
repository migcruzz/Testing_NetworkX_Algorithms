from CsvProcessor.generator import generate_random_graph
from Testers.bi_astar import AStarVsBidirectionalComparison
from Testers.d_star_lite import DStarLiteVsAStarComparison
from Testers.ida_star import IDAStarVsAStarComparison
from Testers.rtaa_star import RTAAStarVsAStarComparison
from Testers.sma_star import SMAStarVsAStarComparison

N_NODES = 1000
N_EDGES = 3000

DIRECTED = False

MIN_WEIGHT = 1
MAX_WEIGHT = 100000

SOURCE = 1
TARGET = 700

graph = generate_random_graph(N_NODES, N_EDGES, DIRECTED, [MIN_WEIGHT, MAX_WEIGHT])

di_graph = graph.to_directed()

"""

df = nx.to_pandas_edgelist(graph)
print("Normal")
print(df)

di_df = nx.to_pandas_edgelist(di_graph)
print("Directed")
print(di_df)

"""

if __name__ == "__main__":
    """
    testerBidirectional = AStarVsBidirectionalComparison(graph, SOURCE, TARGET)
    testerBidirectional.run_all()

    testerDstar = DStarLiteVsAStarComparison(di_graph, SOURCE, TARGET)
    testerDstar.run_all()
    
    
    
    
     testerSma = SMAStarVsAStarComparison(graph, SOURCE, TARGET)
    testerSma.run_all()

    testerIda = IDAStarVsAStarComparison(graph, SOURCE, TARGET)
    testerIda.run_all()
    
    """

    testerBidirectional = AStarVsBidirectionalComparison(graph, SOURCE, TARGET)
    testerBidirectional.run_all()

    testerDstar = DStarLiteVsAStarComparison(di_graph, SOURCE, TARGET)
    testerDstar.run_all()

    testerRtaa = RTAAStarVsAStarComparison(graph, SOURCE, TARGET)
    testerRtaa.run_all()

    testerRtaa2 = RTAAStarVsAStarComparison(graph, SOURCE, TARGET, 50, 30)
    testerRtaa2.run_all()

    testerSma = SMAStarVsAStarComparison(graph, SOURCE, TARGET)
    testerSma.run_all()

    testerIda = IDAStarVsAStarComparison(graph, SOURCE, TARGET)
    testerIda.run_all()
