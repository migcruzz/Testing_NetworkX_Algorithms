import pandas as pd
import networkx as nx

def generate_graph_from_csv(csv_path: str, weight_field: str = "distance_km", directed=False) -> nx.Graph:
    df = pd.read_csv(csv_path)

    G = nx.DiGraph() if directed else nx.Graph()

    for _, row in df.iterrows():
        src = row['origin_city']
        dst = row['destination_city']
        weight = float(row[weight_field])
        G.add_edge(src, dst, weight=weight)

    return G
