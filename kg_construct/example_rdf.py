import csv
from rdflib import Graph, URIRef, Namespace, RDF, OWL
from urllib.parse import quote
from rdflib.plugins.sparql import prepareQuery

# Create a graph and define namespaces
ontology = Graph()
ex = Namespace("")
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
add_triples_from_csv("dsa3101-materials/kg_construct/test_graph.csv", ontology, ex)

if __name__ == "__main__":
    # Output RDF/OWL graph in Turtle format (for visualization)
    print("Ontology in Turtle format:")
    print(ontology.serialize(format='turtle'))

    # Example query to find all courses a specific student is enrolled in
    q = prepareQuery("""
        SELECT ?course WHERE {
        ?student <enrolledIn> ?course .
        }
        """, initNs={"ex": ex})

    print("\nQuery Results:")
    for row in ontology.query(q):
        print(f"Student is enrolled in: {row.course}")