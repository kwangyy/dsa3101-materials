from rdflib import Graph, URIRef, RDF, RDFS
from collections import defaultdict

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

# A function to count the total number of instances in the entire ontology
def count_total_instances(ontology_graph):
    total_instances = 0
    for instance, _, class_type in ontology_graph.triples((None, RDF.type, None)):
        total_instances += 1
    return total_instances

# A function to get direct instances of a given class (excluding subclass instances)
def get_direct_instances(ontology_graph, main_class):
    direct_instances = []
    for instance, _, class_type in ontology_graph.triples((None, RDF.type, main_class)):
        direct_instances.append(instance)
    return direct_instances

# A function to compute the Class Instantiation Metric with the correct hierarchy handling
def compute_class_instantiation_metric(ontology_graph, main_class, total_instances):
    # Get direct instances for the main class
    direct_instances = get_direct_instances(ontology_graph, main_class)
    direct_instance_count = len(direct_instances)

    print(f"\n=== Counting direct instances for {main_class} ===")
    print(f"Direct instances: {direct_instance_count}")

    # Count the total number of instances in the ontology
    total_instances = count_total_instances(ontology_graph)
    print(f"\nTotal instances in the ontology: {total_instances}")

    # Now calculate the metric
    class_instantiation_metric = 0

    # Contribution from the main class itself
    if total_instances > 0:
        main_class_weight = direct_instance_count / total_instances
        class_instantiation_metric += main_class_weight
        print(f"\nDirect contribution from {main_class}: {main_class_weight}")

    # Contributions from subclasses
    print("\n=== Calculating contributions from subclasses ===")
    for subclass in ontology_graph.subjects(RDFS.subClassOf, main_class):
        subclass_direct_instances = get_direct_instances(ontology_graph, subclass)
        subclass_instance_count = len(subclass_direct_instances)
        subclass_depth = get_class_depth(ontology_graph, subclass, main_class)

        if total_instances > 0 and subclass_instance_count > 0:
            subclass_weight = subclass_instance_count / total_instances
            subclass_metric_contribution = subclass_weight / (2 ** subclass_depth)
            class_instantiation_metric += subclass_metric_contribution
            print(f"\nSubclass: {subclass}")
            print(f"  Depth (d(i)): {subclass_depth}")
            print(f"  Direct instances: {subclass_instance_count}")
            print(f"  Proportion of total instances (ir(i)): {subclass_weight}")
            print(f"  Contribution to metric (with depth penalty): {subclass_metric_contribution}")

    print(f"\nFinal Class Instantiation Metric for {main_class}: {class_instantiation_metric}")
    return class_instantiation_metric

# Function to get all unique classes in the ontology
def get_all_classes(ontology_graph):
    classes = set()
    for _, _, class_type in ontology_graph.triples((None, RDF.type, None)):
        classes.add(class_type)
    return classes

# Function to compute the Class Instantiation Metric for all classes in the ontology
def compute_metrics_for_all_classes(ontology_graph):
    total_instances = count_total_instances(ontology_graph)  # Get total instances in the ontology
    all_classes = get_all_classes(ontology_graph)
    
    # Iterate through each class and compute the Class Instantiation Metric
    for cls in all_classes:
        print(f"\n==== Processing Class: {cls} ====")
        compute_class_instantiation_metric(ontology_graph, cls, total_instances)

# Compute the Class Instantiation Metric for all classes in the ontology
compute_metrics_for_all_classes(ontology)


# Function to compute the weighted average metric for all classes in the ontology
def compute_total_metric(ontology_graph):
    total_instances = count_total_instances(ontology_graph)  # Get total instances in the ontology
    all_classes = get_all_classes(ontology_graph)

    total_metric_sum = 0
    for cls in all_classes:
        # Compute the Class Instantiation Metric for each class
        print(f"\n==== Processing Class: {cls} ====")
        class_metric = compute_class_instantiation_metric(ontology_graph, cls, total_instances)
        
        # Sum the class metrics directly (no weighting needed)
        total_metric_sum += class_metric
    
    return total_metric_sum

# Compute the Class Instantiation Metric for all classes in the ontology
print("The class instantiation metric for this ontology: ", compute_total_metric(ontology))