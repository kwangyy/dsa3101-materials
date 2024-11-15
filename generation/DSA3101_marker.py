import json
from collections import defaultdict
from typing import Dict, List, Set, Tuple
import difflib
from dataclasses import dataclass
import numpy as np

@dataclass
class EvaluationMetrics:
    precision: float
    recall: float
    f1_score: float
    exact_matches: int
    partial_matches: int
    missing_entries: int
    extra_entries: int

class NERRelationshipEvaluator:
    def __init__(self, ground_truth: Dict, prediction: Dict):
        # Handle case where prediction is nested under 'data'
        if 'data' in prediction:
            prediction = prediction['data']
        if 'data' in ground_truth:
            ground_truth = ground_truth['data']
        
            
        self.ground_truth = self._normalize_json(ground_truth)
        self.prediction = self._normalize_json(prediction)
    
    def _normalize_json(self, data: Dict) -> Dict:
        """Normalize JSON by sorting all lists and standardizing formats, handling null values"""
        normalized = data.copy()
        
        # Handle entities section
        if 'entities' in normalized:
            for entity_type in ['persons', 'organizations', 'roles', 'products_services']:
                if entity_type in normalized.get('entities', {}):
                    # Filter out any null entries and handle null fields
                    normalized['entities'][entity_type] = sorted(
                        [entry for entry in normalized['entities'][entity_type] if entry is not None],
                        key=lambda x: (x.get('name', x.get('title', '')).lower() if x.get('name') or x.get('title') else '')
                    )
        
        # Handle relationships section
        if 'relationships' in normalized:
            # Filter out any null relationships
            relationships = [rel for rel in normalized['relationships'] if rel is not None]
            normalized['relationships'] = sorted(
                relationships,
                key=lambda x: (
                    x.get('type', '').lower() if x.get('type') else '',
                    x.get('person', '').lower() if x.get('person') else '',
                    self._normalize_organization_name(x.get('organization', '')).lower() if x.get('organization') else '',
                    x.get('role', '').lower() if x.get('role') else '',
                    x.get('product_service', '').lower() if x.get('product_service') else '',
                    x.get('location', '').lower() if x.get('location') else ''
                )
            )
        
        return normalized

    def _normalize_organization_name(self, org_name: str) -> str:
        """Strip department information from organization names, handling null values"""
        if not org_name:
            return ""
        if isinstance(org_name, str):
            return org_name.split(',')[0].strip()
        return ""
    
    def evaluate_entities(self, entity_type: str) -> EvaluationMetrics:
        """Evaluate specific entity type with order independence"""
        # Convert to sets for order-independent comparison
        gt_entities = {self._normalize_entity(item, entity_type) for item in 
                      self.ground_truth["entities"].get(entity_type, [])}
        pred_entities = {self._normalize_entity(item, entity_type) for item in 
                        self.prediction["entities"].get(entity_type, [])}
        
        exact_matches = len(gt_entities & pred_entities)
        partial_matches = self._find_partial_matches(gt_entities - pred_entities, 
                                                   pred_entities - gt_entities)
        
        precision = exact_matches / len(pred_entities) if pred_entities else 0
        recall = exact_matches / len(gt_entities) if gt_entities else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) else 0
        
        return EvaluationMetrics(
            precision=precision,
            recall=recall,
            f1_score=f1,
            exact_matches=exact_matches,
            partial_matches=partial_matches,
            missing_entries=len(gt_entities - pred_entities),
            extra_entries=len(pred_entities - gt_entities)
        )
    
    def _normalize_entity(self, entity: Dict, entity_type: str) -> str:
        """Convert entity to comparable string format"""
        if 'name' in entity:
            name = entity['name'].lower()
            if entity_type == 'organizations':
                name = self._normalize_organization_name(name)
            return f"name:{name}"
        elif 'title' in entity:
            # For roles, strip out department info
            title = entity['title'].split(',')[0].strip().lower()
            return f"title:{title}"
        return ""
    
    def evaluate_relationships(self) -> EvaluationMetrics:
        """Evaluate relationships with order independence"""
        gt_relationships = self._normalize_relationships(self.ground_truth["relationships"])
        pred_relationships = self._normalize_relationships(self.prediction["relationships"])
        
        exact_matches = len(gt_relationships & pred_relationships)
        partial_matches = self._find_relationship_partial_matches(
            gt_relationships - pred_relationships,
            pred_relationships - gt_relationships
        )
        
        precision = exact_matches / len(pred_relationships) if pred_relationships else 0
        recall = exact_matches / len(gt_relationships) if gt_relationships else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) else 0
        
        return EvaluationMetrics(
            precision=precision,
            recall=recall,
            f1_score=f1,
            exact_matches=exact_matches,
            partial_matches=partial_matches,
            missing_entries=len(gt_relationships - pred_relationships),
            extra_entries=len(pred_relationships - gt_relationships)
        )

    def _normalize_relationships(self, relationships: List[Dict]) -> Set[Tuple]:
        """Convert relationships to comparable tuples, normalizing and sorting components"""
        normalized = set()
        for rel in relationships:
            # Extract base role without department info, handle null values
            role = rel.get("role", "").split(",")[0].strip().lower() if rel.get("role") else ""
            # Normalize organization name, handle null values
            organization = self._normalize_organization_name(rel.get("organization", "")).lower() if rel.get("organization") else ""
            
            # Create tuple of components, sorted within each relationship
            # Handle potential null values for all fields
            components = [
                rel.get("type", "").lower(),
                rel.get("person", "").lower(),
                organization,
                role,
                rel.get("product_service", "").lower(),
                rel.get("location", "").lower() if rel.get("location") else ""
            ]
            normalized.add(tuple(components))
        return normalized

    def _find_partial_matches(self, gt_minus_pred: Set[str], pred_minus_gt: Set[str]) -> int:
        """Find similar but not exact matches using string similarity"""
        partial_matches = 0
        for gt_item in gt_minus_pred:
            for pred_item in pred_minus_gt:
                similarity = difflib.SequenceMatcher(None, gt_item, pred_item).ratio()
                if similarity > 0.8:  # Threshold for considering partial match
                    partial_matches += 1
                    break
        return partial_matches

    def _find_relationship_partial_matches(self, gt_minus_pred: Set[Tuple], 
                                         pred_minus_gt: Set[Tuple]) -> int:
        """Find relationships that match in entities but differ in type or details"""
        partial_matches = 0
        for gt_rel in gt_minus_pred:
            for pred_rel in pred_minus_gt:
                # Compare all fields except relationship type
                gt_entities = set(gt_rel[1:])  # Exclude relationship type
                pred_entities = set(pred_rel[1:])
                if len(gt_entities & pred_entities) >= len(gt_entities) - 1:  # Allow one field to differ
                    partial_matches += 1
                    break
        return partial_matches

def evaluate_model_output(ground_truth_json: Dict, prediction_json: Dict) -> Dict:
    evaluator = NERRelationshipEvaluator(ground_truth_json, prediction_json)
    report = {
        "entity_metrics": {},
        "relationship_metrics": None,
        "overall_metrics": {}
    }
    
    # Evaluate each entity type
    for entity_type in ["persons", "organizations", "roles", "products_services"]:
        metrics = evaluator.evaluate_entities(entity_type)
        report["entity_metrics"][entity_type] = metrics.__dict__
    
    # Evaluate relationships
    relationship_metrics = evaluator.evaluate_relationships()
    report["relationship_metrics"] = relationship_metrics.__dict__
    
    # Calculate overall metrics
    all_metrics = list(report["entity_metrics"].values()) + [relationship_metrics.__dict__]
    report["overall_metrics"] = {
        "precision": np.mean([m["precision"] for m in all_metrics]),
        "recall": np.mean([m["recall"] for m in all_metrics]),
        "f1_score": np.mean([m["f1_score"] for m in all_metrics])
    }
    
    return report

ground_truth_filepath = "response_100.json"
prediction_filepath = "response_100_evaluated.json"


def load_json(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)
    
# Load the JSON data from the files
ground_truth = load_json(ground_truth_filepath)
prediction = load_json(prediction_filepath)

report = evaluate_model_output(ground_truth, prediction)
