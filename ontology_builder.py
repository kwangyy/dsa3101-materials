import csv
from rdflib import Graph, URIRef, Namespace, RDF, RDFS, OWL
from urllib.parse import quote

# Create a graph and define namespaces
ontology = Graph()
ex = Namespace("http://example.org/")
ontology.bind("ex", ex)

# Define the class hierarchy: Human -> FacultyMember, Student
ontology.add((URIRef(ex["FacultyMember"]), RDFS.subClassOf, URIRef(ex["Human"])))
ontology.add((URIRef(ex["Student"]), RDFS.subClassOf, URIRef(ex["Human"])))

# Define the class hierarchy: Building -> Department -> Course
ontology.add((URIRef(ex["Department"]), RDFS.subClassOf, URIRef(ex["Building"])))
ontology.add((URIRef(ex["Course"]), RDFS.subClassOf, URIRef(ex["Department"])))

# Function to add triples from CSV to the RDF graph and assign classes
def add_triples_and_classes_from_csv(csv_file, rdf_graph, namespace):
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            head_node = URIRef(namespace[quote(row['head_node'])])
            relationship = URIRef(namespace[quote(row['relationship'])])
            tail_node = URIRef(namespace[quote(row['tail_node'])])

            # Add the triple (head_node, relationship, tail_node)
            rdf_graph.add((head_node, relationship, tail_node))

            # Class inference based on the relationship for head_node
            if row['relationship'] == "teaches" or row['relationship'] == "worksIn":
                # Assign FacultyMember class for these relationships
                rdf_graph.add((head_node, RDF.type, URIRef(namespace["FacultyMember"])))
            elif row['relationship'] == "enrolledIn":
                # Assign Student class for this relationship
                rdf_graph.add((head_node, RDF.type, URIRef(namespace["Student"])))
            
            # Class inference based on the relationship for tail_node
            if row['relationship'] in ["teaches", "enrolledIn", "offers"]:
                # If the tail_node is a course
                rdf_graph.add((tail_node, RDF.type, URIRef(namespace["Course"])))
            elif row['relationship'] == "locatedIn":
                # If the head_node is a department and the tail_node is a building
                rdf_graph.add((head_node, RDF.type, URIRef(namespace["Department"])))
                rdf_graph.add((tail_node, RDF.type, URIRef(namespace["Building"])))

            # Mark relationships as ObjectProperties
            rdf_graph.add((relationship, RDF.type, OWL.ObjectProperty))

# Add triples and class information from the CSV file to the RDF graph
add_triples_and_classes_from_csv('kg_construct/test_graph.csv', ontology, ex)

# Save the RDF graph to a file (in Turtle format)
ontology.serialize("kg_construct/ontology_graph.ttl", format='turtle')

print("Ontology saved to kg_construct/ontology_graph.ttl")
