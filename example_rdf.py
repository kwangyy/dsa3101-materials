from rdflib import Graph, Literal, RDF, URIRef, Namespace, OWL
from rdflib.plugins.sparql import prepareQuery

# Step 1: Create a graph and define namespaces
g = Graph()

# Define the namespace (use your own domain here)
ex = Namespace("http://example.org/university#")
g.bind("ex", ex)

# Step 2: Define individuals (resources)
john = URIRef(ex.John)           # John, a student
course = URIRef(ex.CS101)        # CS101, a course
professor = URIRef(ex.ProfessorSmith)  # Professor Smith

# Step 3: Define relationships (properties)
teaches = URIRef(ex.teaches)     # Professor teaches Course
enrolls_in = URIRef(ex.enrollsIn)  # Student enrolls in Course

# Step 4: Add triples to the graph (RDF triples)
g.add((john, RDF.type, URIRef(ex.Student)))       # John is a Student
g.add((course, RDF.type, URIRef(ex.Course)))      # CS101 is a Course
g.add((professor, RDF.type, URIRef(ex.Professor))) # Professor Smith is a Professor
g.add((professor, teaches, course))               # Professor Smith teaches CS101
g.add((john, enrolls_in, course))                 # John enrolls in CS101

# Step 5: Define OWL classes and object properties
g.add((ex.Professor, RDF.type, OWL.Class))        # Define Professor as a class
g.add((ex.Student, RDF.type, OWL.Class))          # Define Student as a class
g.add((ex.Course, RDF.type, OWL.Class))           # Define Course as a class
g.add((teaches, RDF.type, OWL.ObjectProperty))    # Define teaches as an ObjectProperty
g.add((enrolls_in, RDF.type, OWL.ObjectProperty)) # Define enrollsIn as an ObjectProperty

# Step 6: Define relationships between classes (using OWL)
g.add((ex.Professor, OWL.disjointWith, ex.Student))  # Professors cannot be Students

# Step 7: Output RDF/OWL graph in Turtle format (for visualization)
print("Ontology in Turtle format:")
print(g.serialize(format='turtle').encode('utf-8'))


# Step 8: Query the graph using SPARQL
# Example query to find all courses John is enrolled in
q = prepareQuery("""
    SELECT ?course WHERE {
      ?student ex:enrollsIn ?course .
    }
    """, initNs={"ex": ex})

print("\nQuery Results:")
for row in g.query(q):
    print(f"John is enrolled in: {row.course}")
