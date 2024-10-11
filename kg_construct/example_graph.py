import networkx as nx 
import pandas as pd 
import matplotlib.pyplot as plt

kg_data = pd.read_csv("dsa3101-materials/kg_construct/test_graph.csv")
data_graph = nx.Graph()
for _, row in kg_data.iterrows():
    data_graph.add_edge(row['head_node'], row['tail_node'], label=row['relationship'])


pos = nx.spring_layout(data_graph, seed=42, k=0.9)
labels = nx.get_edge_attributes(data_graph, 'label')

if __name__ == "__main__":
    plt.figure(figsize=(12, 10))
    nx.draw(data_graph, pos, with_labels=True, font_size=10, node_size=700, node_color='lightblue', edge_color='gray', alpha=0.6)
    nx.draw_networkx_edge_labels(data_graph, pos, edge_labels=labels, font_size=8, label_pos=0.3, verticalalignment='baseline')
    plt.title('Knowledge Graph')
    plt.show()