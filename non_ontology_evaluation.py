import networkx as nx
import matplotlib.pyplot as plt  # Import matplotlib for plotting
from ontology_evaluation import evaluate_graph_completeness, evaluate_graph_consistency, evaluate_query_performance, generate_non_ontology_knowledge_graph, ex

# Non-ontology data
non_ontology_data = [
    ("Company A", "locatedIn", "Country X"),
    ("John", "supervises", "Jane"),
    ("Building Y", "offers", "Service Z"),
    ("Park", "locatedIn", "City Z")
]

# Generate a knowledge graph from the non-ontology dataset
non_ontology_graph = generate_non_ontology_knowledge_graph(non_ontology_data)

# Evaluate the non-ontology dataset
print("Evaluating Non-Ontology Dataset:")

# Expected labels from the ontology-based setup
expected_node_types = {ex.Person, ex.Course, ex.Department, ex.Building}

# Evaluate completeness (expected to be poor)
evaluate_graph_completeness(non_ontology_graph, expected_node_types)

# Evaluate consistency (expected to be poor)
evaluate_graph_consistency(non_ontology_graph)

# Example queries for non-ontology dataset
example_queries_non_ontology = [
    ("John", "supervises", "Jane"),
    ("Company A", "locatedIn", "Country X")
]
evaluate_query_performance(non_ontology_graph, example_queries_non_ontology)

# Visualize the non-ontology graph
plt.figure(figsize=(12, 10))
pos = nx.spring_layout(non_ontology_graph, k=0.5, iterations=50)
nx.draw(non_ontology_graph, pos, with_labels=True, font_size=10, node_size=3000, node_color='lightcoral', edge_color='gray', alpha=0.6)
edge_labels = nx.get_edge_attributes(non_ontology_graph, 'label')
nx.draw_networkx_edge_labels(non_ontology_graph, pos, edge_labels=edge_labels)
plt.title('Non-Ontology Knowledge Graph')
plt.show()
