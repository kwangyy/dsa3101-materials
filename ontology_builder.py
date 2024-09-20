import csv
from rdflib import Graph, URIRef, Namespace, RDF, OWL  # Import URIRef
from urllib.parse import quote

# Create a graph and define namespaces
ontology = Graph()
ex = Namespace("http://example.org/")
ontology.bind("ex", ex)

# Function to add triples from CSV to the RDF graph
def add_triples_from_csv(csv_file, rdf_graph, namespace):
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            head_node = URIRef(namespace[quote(row['head_node'])])
            relationship = URIRef(namespace[quote(row['relationship'])])
            tail_node = URIRef(namespace[quote(row['tail_node'])])

            rdf_graph.add((head_node, relationship, tail_node))
            
            # Optionally, infer and add types for nodes and relationships
            rdf_graph.add((relationship, RDF.type, OWL.ObjectProperty))

# Add triples from the CSV file to the RDF graph
add_triples_from_csv('kg_construct/test_graph.csv', ontology, ex)

# Save the RDF graph to a file (in Turtle format)
ontology.serialize("kg_construct/ontology_graph.ttl", format='turtle')

print("Ontology saved to kg_construct/ontology_graph.ttl")
