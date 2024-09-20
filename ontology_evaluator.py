from rdflib import Graph, URIRef, RDF, RDFS  # Import URIRef
from collections import defaultdict
import math

# Load the saved ontology from the Turtle file
ontology = Graph()
ontology.parse("kg_construct/ontology_graph.ttl", format="turtle")

# A helper function to recursively compute the depth of subclasses
def get_class_depth(ontology_graph, subclass, main_class, depth=0):
    if subclass == main_class:
        return depth
    for superclass in ontology_graph.objects(subclass, RDFS.subClassOf):
        return get_class_depth(ontology_graph, superclass, main_class, depth + 1)
    return None  # Return None if no superclass is found

# A function to compute the Class Instantiation Metric
def compute_class_instantiation_metric(ontology_graph, main_class):
    instance_counts = defaultdict(int)
    total_instances = 0

    for instance, _, class_type in ontology_graph.triples((None, RDF.type, None)):
        if (class_type, RDFS.subClassOf, main_class) in ontology_graph or class_type == main_class:
            instance_counts[class_type] += 1
            total_instances += 1

    class_instantiation_metric = 0
    for subclass, count in instance_counts.items():
        depth = get_class_depth(ontology_graph, subclass, main_class)
        if depth is not None:
            ir_i = count / total_instances
            metric_contribution = ir_i / (2 ** depth)
            class_instantiation_metric += metric_contribution

    return class_instantiation_metric

# Define your main class (e.g., Person)
main_class = URIRef("http://example.org/Person")

# Compute the Class Instantiation Metric
metric_value = compute_class_instantiation_metric(ontology, main_class)
print(f"Class Instantiation Metric: {metric_value}")
