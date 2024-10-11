import networkx as nx
from rdflib import Graph, RDF, URIRef, Namespace
from rdflib.namespace import RDFS, OWL
import matplotlib.pyplot as plt
from example_graph import data_graph, pos, labels
from example_rdf import ontology, ex
from urllib.parse import quote, unquote
import csv

# Create a graph and define namespaces
ontology = Graph()
ex = Namespace("")
ontology.bind("ex", ex)

# Function to add triples from CSV to the RDF graph
def add_triples_from_csv(csv_file, rdf_graph, namespace):
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            head_node = URIRef(namespace[quote(unquote(row['head_node']))])
            relationship = URIRef(namespace[quote(unquote(row['relationship']))])
            tail_node = URIRef(namespace[quote(unquote(row['tail_node']))])
            
            rdf_graph.add((head_node, relationship, tail_node))
            
            # Optionally, infer and add types for nodes and relationships
            rdf_graph.add((relationship, RDF.type, OWL.ObjectProperty))

# Add triples from the CSV file to the RDF graph
add_triples_from_csv('dsa3101-materials/kg_construct/test_graph.csv', ontology, ex)

def validate_and_convert_graph(nx_graph, rdf_ontology):
    validated_graph = Graph()
    validated_graph += rdf_ontology

    edges_to_remove = []

    for head, tail, edge_data in nx_graph.edges(data=True):
        relationship = edge_data['label']
        
        # Convert node names and relationships to valid URIs
        head_uri = URIRef(ex[quote(unquote(head))])
        tail_uri = URIRef(ex[quote(unquote(tail))])
        relationship_uri = URIRef(ex[quote(unquote(relationship))])

        if (relationship_uri, RDF.type, OWL.ObjectProperty) not in rdf_ontology:
            # Mark this edge for removal
            edges_to_remove.append((head, tail))
            continue

        validated_graph.add((head_uri, relationship_uri, tail_uri))

        for node, uri in [(head, head_uri), (tail, tail_uri)]:
            node_type = infer_node_type(uri, relationship_uri, rdf_ontology)
            if node_type:
                validated_graph.add((uri, RDF.type, node_type))

    # Remove edges that do not exist in the ontology
    nx_graph.remove_edges_from(edges_to_remove)

    return validated_graph

def infer_node_type(node_uri, relationship_uri, ontology):
    for s, p, o in ontology.triples((relationship_uri, RDFS.domain, None)):
        return o
    for s, p, o in ontology.triples((relationship_uri, RDFS.range, None)):
        return o
    return None

def rdf_to_networkx(rdf_graph):
    G = nx.Graph()
    exclude_properties = {RDF.type, OWL.disjointWith}  # Add more properties to exclude as needed
    for s, p, o in rdf_graph:
        if isinstance(o, URIRef) and p not in exclude_properties:  # Exclude specific properties
            G.add_edge(str(s), str(o), label=str(p))
    return G

# Create a NetworkX graph from the RDF graph
data_graph = rdf_to_networkx(ontology)

# Validate and convert the NetworkX graph to an RDF graph
validated_rdf_graph = validate_and_convert_graph(data_graph, ontology)

# Output the validated graph in Turtle format
print("Validated and combined graph in Turtle format:")
print(validated_rdf_graph.serialize(format='turtle'))

# Convert the validated RDF graph back to a NetworkX graph for visualization
nx_validated_graph = rdf_to_networkx(validated_rdf_graph)

if __name__ == "__main__":
    # Visualize the graph
    plt.figure(figsize=(12, 10))
    pos = nx.spring_layout(nx_validated_graph, k=0.5, iterations=50)
    nx.draw(nx_validated_graph, pos, with_labels=False, font_size=8, node_size=3000, node_color='lightblue', 
            edge_color='gray', alpha=0.6, arrows=True)

    # Add edge labels
    edge_labels = nx.get_edge_attributes(nx_validated_graph, 'label')
    nx.draw_networkx_edge_labels(nx_validated_graph, pos, edge_labels=edge_labels, font_size=6)

    # Improve node labels
    labels = {node: node.split('/')[-1].replace('>', '') for node in nx_validated_graph.nodes()}
    labels = {k: v.replace('%20', ' ') for k, v in labels.items()}  # Replace URL encoding for spaces
    nx.draw_networkx_labels(nx_validated_graph, pos, labels, font_size=8)

    plt.title('Validated Knowledge Graph')
    plt.axis('off')
    plt.tight_layout()
    plt.show()