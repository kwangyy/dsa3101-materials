def evaluate_graph_completeness(triplets, ontology):
    """Evaluate completeness of graph against ontology"""
    # Get expected types from ontology
    expected_types = set(entity['type'] for entity in ontology['ontology']['entities'])
    
    # Track present types from triplets
    present_types = set()
    for triplet in triplets:
        for rel in ontology['ontology']['relationships']:
            if rel['type'] == triplet['type']:
                present_types.add(rel['from'])
                present_types.add(rel['to'])
                break
    
    completeness_score = len(present_types) / len(expected_types)
    
    print(f"Completeness Score: {completeness_score:.2f}")
    if missing := (expected_types - present_types):
        print(f"Missing entity types: {missing}")
        
    return completeness_score

def evaluate_graph_consistency(triplets, ontology):
    """Evaluate consistency of relationships and properties"""
    ontology_dict = create_ontology_dict(ontology)
    invalid_count = 0
    
    for triplet in triplets:
        rel_type = triplet['type']
        entity_keys = [k for k in triplet.keys() if k != 'type']
        
        # Validate relationship exists and entities match expected types
        valid = False
        for rel in ontology['ontology']['relationships']:
            if rel['type'] == rel_type:
                if len(entity_keys) == 2:
                    # Verify relationship is valid for these entity types
                    head_type = rel['from']
                    tail_type = rel['to']
                    if (head_type in ontology_dict and 
                        tail_type in ontology_dict[head_type] and
                        rel_type in ontology_dict[head_type][tail_type]):
                        valid = True
                break
        
        if not valid:
            invalid_count += 1
            print(f"Invalid relationship: {triplet}")
    
    consistency_score = 1 - (invalid_count / len(triplets)) if triplets else 0
    print(f"Consistency Score: {consistency_score:.2f}")
    
    return consistency_score

def create_ontology_dict(ontology_json):
    """Create a dictionary of valid relationships from ontology JSON"""
    ontology_dict = {}
    
    # Map relationships from JSON structure
    for rel in ontology_json['ontology']['relationships']:
        head_type = rel['from']
        tail_type = rel['to']
        relationship = rel['type']
        
        if head_type not in ontology_dict:
            ontology_dict[head_type] = {}
        if tail_type not in ontology_dict[head_type]:
            ontology_dict[head_type][tail_type] = set()
            
        ontology_dict[head_type][tail_type].add(relationship)
    
    return ontology_dict

def create_entity_mapping(ontology_json):
    """Create entity type mapping from ontology"""
    mapping = {}
    for entity in ontology_json['ontology']['entities']:
        # Convert entity type to lowercase for field name matching
        field_name = entity['type'].lower().replace('/', '_')
        mapping[field_name] = entity['type']
    return mapping

def evaluate_ner_relationships(response_json, ontology_json):
    """Evaluate NER relationships against ontology using JSON input"""
    ontology_dict = create_ontology_dict(ontology_json)
    entity_mapping = create_entity_mapping(ontology_json)
    
    # Initialize counters
    total_valid = 0
    total_invalid = 0
    invalid_cases = []
    
    # Process relationships from response JSON
    relationships = response_json['data']['relationships']
    
    for rel in relationships:
        relationship_type = rel['type']
        
        # Find head and tail entities and their types
        head_type = None
        tail_type = None
        head_entity = None
        tail_entity = None
        
        for field, value in rel.items():
            if field != 'type':
                if head_entity is None:
                    head_entity = value
                    head_type = entity_mapping.get(field)
                else:
                    tail_entity = value
                    tail_type = entity_mapping.get(field)
        
        # Validate relationship
        is_valid = (
            head_type in ontology_dict and 
            tail_type in ontology_dict[head_type] and 
            relationship_type in ontology_dict[head_type][tail_type]
        )
        
        if is_valid:
            total_valid += 1
        else:
            total_invalid += 1
            invalid_cases.append({
                'head': head_entity,
                'head_type': head_type,
                'relationship': relationship_type,
                'tail': tail_entity,
                'tail_type': tail_type
            })
    
    # Calculate metrics
    total_rows = total_valid + total_invalid
    accuracy = (total_valid / total_rows) * 100 if total_rows > 0 else 0

    return {
        'accuracy': accuracy,
        'valid_count': total_valid,
        'invalid_count': total_invalid,
        'invalid_cases': invalid_cases
    }

def evaluate_all_metrics(response_json, ontology_json):
    """
    Comprehensive evaluation function that combines completeness, consistency, and accuracy metrics
    
    Args:
        response_json: JSON containing the NER results
        ontology_json: JSON containing the ontology definition
    
    Returns:
        dict: Combined metrics and detailed results
    """
    # Get relationships from response
    relationships = response_json['data']['relationships']
    
    # Evaluate completeness
    completeness_score = evaluate_graph_completeness(relationships, ontology_json)
    
    # Evaluate consistency
    consistency_score = evaluate_graph_consistency(relationships, ontology_json)
    
    # Evaluate NER relationships
    ner_results = evaluate_ner_relationships(response_json, ontology_json)
    
    # Combine all metrics
    combined_metrics = {
        'completeness_score': completeness_score,
        'consistency_score': consistency_score,
        'accuracy': ner_results['accuracy'],
        'valid_count': ner_results['valid_count'],
        'invalid_count': ner_results['invalid_count'],
        'invalid_cases': ner_results['invalid_cases'],
        'overall_score': (completeness_score + consistency_score + (ner_results['accuracy']/100)) / 3
    }
    
    # Print comprehensive summary
    print("\nComprehensive Evaluation Summary:")
    print(f"Completeness Score: {combined_metrics['completeness_score']:.2f}")
    print(f"Consistency Score: {combined_metrics['consistency_score']:.2f}")
    print(f"Accuracy: {combined_metrics['accuracy']:.2f}%")
    print(f"Valid Relationships: {combined_metrics['valid_count']}")
    print(f"Invalid Relationships: {combined_metrics['invalid_count']}")
    print(f"Overall Score: {combined_metrics['overall_score']:.2f}")
    
    if combined_metrics['invalid_cases']:
        print("\nDetailed Invalid Cases:")
        for case in combined_metrics['invalid_cases']:
            print(f"Invalid: {case['head_type']} -[{case['relationship']}]-> {case['tail_type']}")
            print(f"  Entities: {case['head']} -> {case['tail']}")
    
    return combined_metrics
