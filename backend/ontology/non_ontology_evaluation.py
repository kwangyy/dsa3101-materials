import json
import networkx as nx
import matplotlib.pyplot as plt
from ontology_evaluation import evaluate_graph_completeness, evaluate_graph_consistency

def generate_non_ontology_knowledge_graph(data):
    """Generate a NetworkX graph from non-ontology data"""
    G = nx.DiGraph()
    
    for triplet in data:
        source, relation, target = triplet
        G.add_edge(source, target, label=relation)
    
    return G

def visualize_graph(G, title="Knowledge Graph"):
    """Visualize the knowledge graph"""
    plt.figure(figsize=(12, 10))
    pos = nx.spring_layout(G, k=0.5, iterations=50)
    
    # Draw nodes
    nx.draw(G, pos, 
           with_labels=True,
           font_size=10,
           node_size=3000,
           node_color='lightblue',
           edge_color='gray',
           alpha=0.6)
    
    # Draw edge labels
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    
    plt.title(title)
    plt.show()

def evaluate_non_ontology_data(data, ontology):
    """Evaluate non-ontology data against our ontology structure"""
    # Convert data to format matching our ontology structure
    converted_triplets = []
    for source, relation, target in data:
        triplet = {
            "type": relation,
            "person": source if "Person" in ontology["ontology"]["entities"] else None,
            "organization": source if "Organization" in source else target if "Organization" in target else None,
            "role": target if "Role" in target else None,
            "product_service": target if "Product" in target or "Service" in target else None,
            "location": target if "Location" in target else None
        }
        # Remove None values
        triplet = {k: v for k, v in triplet.items() if v is not None}
        if len(triplet) > 1:  # Must have at least type and one other field
            converted_triplets.append(triplet)
    
    # Evaluate using existing metrics
    completeness = evaluate_graph_completeness(converted_triplets, ontology)
    consistency = evaluate_graph_consistency(converted_triplets, ontology)
    
    return {
        "completeness": completeness,
        "consistency": consistency,
        "triplets_analyzed": len(converted_triplets),
        "original_triplets": len(data)
    }

if __name__ == "__main__":
    # Example non-ontology data (relationships that might not match our ontology)
    non_ontology_data = [
        ("John Smith", "WORKS_AT", "Tech Corp"),
        ("Tech Corp", "BASED_IN", "New York"),
        ("Sarah Jones", "MANAGES", "Product X"),
        ("Tech Corp", "PROVIDES", "Cloud Service"),
        ("Tech Corp", "AFFILIATED_WITH", "Samuel Davis")
    ]
    
    # Load ontology for comparison
    with open('backend/examples/example_ontology.json', 'r') as file:
        ontology_json = json.load(file)
    
    # Evaluate against our ontology
    results = evaluate_non_ontology_data(non_ontology_data, ontology_json)
    
    print("\nEvaluation Results:")
    print(f"Completeness Score: {results['completeness']:.2f}")
    print(f"Consistency Score: {results['consistency']:.2f}")
    print(f"Analyzed Triplets: {results['triplets_analyzed']}/{results['original_triplets']}")
