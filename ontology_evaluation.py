import networkx as nx
from rdflib import Graph, RDF, URIRef, Namespace
from rdflib.namespace import RDFS, OWL
import matplotlib.pyplot as plt
from urllib.parse import quote, unquote
import csv

# Create RDF graph and define namespaces
ontology = Graph()
ex = Namespace("")  # Using empty namespace as requested
ontology.bind("ex", ex)

# Explicitly define ontology types if not already present
ontology.add((ex.Person, RDF.type, RDFS.Class))
ontology.add((ex.Course, RDF.type, RDFS.Class))
ontology.add((ex.Department, RDF.type, RDFS.Class))
ontology.add((ex.Building, RDF.type, RDFS.Class))

# Function to add triples from CSV and assign node types to the RDF graph
def add_triples_from_csv(csv_file, rdf_graph, namespace):
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            head_node = URIRef(namespace[quote(unquote(row['head_node']))])
            relationship = URIRef(namespace[quote(unquote(row['relationship']))])
            tail_node = URIRef(namespace[quote(unquote(row['tail_node']))])
            
            # Add triples (head_node - relationship -> tail_node)
            rdf_graph.add((head_node, relationship, tail_node))
            
            # Infer types for head and tail nodes based on the relationship
            assign_node_type(head_node, relationship, rdf_graph, is_subject=True)
            assign_node_type(tail_node, relationship, rdf_graph, is_subject=False)
            
            # Define the relationship as an ObjectProperty
            rdf_graph.add((relationship, RDF.type, OWL.ObjectProperty))

# Function to assign node types based on relationships
def assign_node_type(node_uri, relationship_uri, rdf_graph, is_subject=True):
    """
    Assigns types (labels) to nodes based on the relationships they participate in.
    Ensures that nodes are only assigned one type based on context.
    """
    if is_subject:
        if 'teaches' in str(relationship_uri) or 'worksIn' in str(relationship_uri):
            rdf_graph.add((node_uri, RDF.type, ex.Person))
        elif 'offers' in str(relationship_uri):
            rdf_graph.add((node_uri, RDF.type, ex.Department))
    else:  # Tail node (object)
        if 'enrolledIn' in str(relationship_uri):
            rdf_graph.add((node_uri, RDF.type, ex.Person))
        elif 'teaches' in str(relationship_uri):
            rdf_graph.add((node_uri, RDF.type, ex.Course))
        elif 'offers' in str(relationship_uri):
            rdf_graph.add((node_uri, RDF.type, ex.Course))
        elif 'locatedIn' in str(relationship_uri):
            rdf_graph.add((node_uri, RDF.type, ex.Building))

    # Logging for debugging
    print(f"Assigned type for {node_uri}: {rdf_graph.value(node_uri, RDF.type)}")

# Function to infer node types for existing nodes
def infer_node_type(node_uri, relationship_uri, ontology):
    """
    Infers the type (class) of a node based on the relationship.
    """
    for s, p, o in ontology.triples((relationship_uri, RDFS.domain, None)):
        return o
    for s, p, o in ontology.triples((relationship_uri, RDFS.range, None)):
        return o
    return None

# Add triples from the CSV file to the RDF graph
add_triples_from_csv('dsa3101-materials/kg_construct/test_graph.csv', ontology, ex)

# Check the RDF graph after adding triples and assigning types
print("RDF graph after adding triples and assigning types:")
print(ontology.serialize(format='turtle'))

# Function to validate and convert a NetworkX graph to an RDF graph
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

        # Check if the relationship exists in the ontology
        if (relationship_uri, RDF.type, OWL.ObjectProperty) not in rdf_ontology:
            # Mark this edge for removal if relationship is invalid
            edges_to_remove.append((head, tail))
            continue

        validated_graph.add((head_uri, relationship_uri, tail_uri))

        for node, uri in [(head, head_uri), (tail, tail_uri)]:
            node_type = infer_node_type(uri, relationship_uri, rdf_ontology)
            if node_type:
                validated_graph.add((uri, RDF.type, node_type))

    # Remove invalid edges from the NetworkX graph
    nx_graph.remove_edges_from(edges_to_remove)

    return validated_graph

# Function to convert RDF graph to NetworkX graph
def rdf_to_networkx(rdf_graph):
    G = nx.Graph()

    # Step 1: Add nodes and edges for actual entities (subjects and objects)
    for s, p, o in rdf_graph:
        # Add subjects and objects as nodes (predicates are excluded)
        if isinstance(s, URIRef):  # Subject is always an entity
            G.add_node(str(s))
        if isinstance(o, URIRef) and p != RDF.type:  # Object is an entity, but skip rdf:type
            G.add_node(str(o))

        # Add edge (subject -> object) with predicate as the label
        if isinstance(o, URIRef) and p != RDF.type:
            G.add_edge(str(s), str(o), label=str(p))

        # Assign rdf:type as a label for the subject (without treating rdf:type as a node)
        if p == RDF.type and isinstance(s, URIRef):
            node_type = str(o).split('/')[-1]  # Get the type (Person, Course, etc.)
            G.nodes[str(s)]['label'] = node_type  # Assign the node type as label

    return G

# Function to evaluate the completeness of the graph
def evaluate_graph_completeness(nx_graph, expected_labels):
    """
    Evaluate completeness by checking if all expected node types are present.
    """
    # Extract labels from the nodes in the NetworkX graph
    node_labels = set(data.get('label') for node, data in nx_graph.nodes(data=True) if 'label' in data)

    # Convert expected labels to strings (since they are URIRefs)
    expected_label_strs = set(str(label) for label in expected_labels)

    print(f"expected_labels: {expected_label_strs}")
    print(f"node_labels: {node_labels}")

    # Compute missing labels
    missing_labels = expected_label_strs - node_labels
    completeness_score = (len(expected_label_strs) - len(missing_labels)) / len(expected_label_strs)

    print(f"Completeness Score: {completeness_score:.2f}")
    if missing_labels:
        print(f"Missing node labels: {missing_labels}")
    else:
        print("All expected labels are present.")

# Evaluate graph consistency
def evaluate_graph_consistency(nx_graph):
    """
    Evaluate consistency by ensuring no invalid relationships exist between nodes.
    """
    invalid_relationships = []
    for u, v, edge_data in nx_graph.edges(data=True):
        relationship = edge_data['label']
        if relationship == 'INVALID_RELATIONSHIP':
            invalid_relationships.append((u, v))

    consistency_score = 1 if not invalid_relationships else 1 - (len(invalid_relationships) / nx_graph.number_of_edges())
    print(f"Consistency Score: {consistency_score:.2f}")
    if invalid_relationships:
        print(f"Invalid relationships found: {invalid_relationships}")
    else:
        print("Graph is consistent.")

# Evaluate graph utility
def evaluate_query_performance(nx_graph, queries):
    """
    Evaluate utility by checking how well the graph can answer predefined queries.
    """
    success_count = 0
    for query in queries:
        # Example query structure: (source, relationship, target)
        source, relationship, target = query
        try:
            if nx.has_path(nx_graph, source, target):
                path = nx.shortest_path(nx_graph, source, target)
                success_count += 1
        except nx.NetworkXNoPath:
            continue
    
    utility_score = success_count / len(queries)
    print(f"Utility Score: {utility_score:.2f}")

# Function to generate a knowledge graph for a non-ontology dataset
def generate_non_ontology_knowledge_graph(data):
    G = nx.Graph()
    for head, relationship, tail in data:
        G.add_node(head)
        G.add_node(tail)
        G.add_edge(head, tail, label=relationship)
    return G

if __name__ == "__main__":
    # Create the RDF graph from the CSV and convert it to NetworkX graph
    data_graph = rdf_to_networkx(ontology)

    # Validate and convert the NetworkX graph to an RDF graph
    validated_rdf_graph = validate_and_convert_graph(data_graph, ontology)

    # Convert the validated RDF graph back to a NetworkX graph for visualization
    nx_validated_graph = rdf_to_networkx(validated_rdf_graph)

    # Evaluate the completeness, consistency, and utility of the graph
    expected_node_types = {ex.Person, ex.Course, ex.Department, ex.Building}
    evaluate_graph_completeness(data_graph, expected_node_types)
    evaluate_graph_consistency(data_graph)

    # Example queries for utility evaluation (adjust based on your ontology)
    example_queries = [
        ('Dr.%20Alice%20Smith', 'teaches', 'AI%20101'),
        ('Mathematics', 'offers', 'Calculus%20I')
    ]

    evaluate_query_performance(nx_validated_graph, example_queries)

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