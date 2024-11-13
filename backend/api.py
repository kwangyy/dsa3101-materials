import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from typing import Dict, Any, List, Optional
import uvicorn
from neo4j import GraphDatabase
import asyncio
import json
from fastapi.responses import StreamingResponse


# Local imports 
from llms.inference_model import infer
from llms.query_model import is_query
from llms.ontology_model import generate_ontology
from llms.conversation_model import process_conversation_with_llm
from query.cypher_engine import execute_cypher_query
from query.llama_query import query_generator
from ontology.ontology_evaluation import evaluate_all_metrics

# Load environment variables
load_dotenv()
api_key = os.getenv("HF_TOKEN")
hf_client = InferenceClient("meta-llama/Llama-3.1-8B-Instruct", api_key=api_key)

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Accept"],
)

# Neo4j setup
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

if driver.verify_connectivity():
    print("Neo4j connected successfully")
else:
    print("Failed to connect to Neo4j")

# Request/Response models
class ProcessResponse(BaseModel):
    status: str
    graphId: str

class OntologyRequest(BaseModel):
    graphId: str
    ontology: Dict[str, Any]

class OntologyResponse(BaseModel):
    metrics: Dict[str, Any]
    entityResult: Dict[str, Any]

class MessageRequest(BaseModel):
    currentMessage: str
    conversationHistory: List[Dict[str, str]]
    graphId: str
    graphContext: Dict[str, Any]

    @validator('conversationHistory')
    def validate_conversation_history(cls, v):
        # Filter out any messages with empty content
        return [
            msg for msg in v 
            if isinstance(msg, dict) and 
            isinstance(msg.get('content', ''), str) and 
            msg.get('content', '').strip()
        ]

# Helper functions
def format_conversation_for_llm(conversation_history: List[Dict[str, str]]) -> List[Dict[str, str]]:
    formatted_messages = []
    formatted_messages.append({
        "role": "system",
        "content": "You are a helpful assistant with knowledge about the graph database."
    })
    
    for message in conversation_history:
        role = "system" if message["role"] == "assistant" else message["role"]
        formatted_messages.append({
            "role": role,
            "content": message["content"]
        })
    
    return formatted_messages

async def execute_llama_pipeline(message: str, graph_context: Dict) -> Optional[Dict[str, Any]]:
    try:
        cypher_query = await query_generator(message, graph_context.get("ontology", ""))
        if not cypher_query:
            return None
            
        query_result = execute_cypher_query(cypher_query["cypher_query"])
        print(query_result)
        return {
            "response": query_result,
            "query": cypher_query,
            "source": "llama"
        }
    except Exception as e:
        print(f"LLaMA pipeline error: {str(e)}")
        return None

# Process API endpoints
@app.post("/api/process/data", response_model=ProcessResponse)
async def process_data(text: Dict[str, Any]):
    try:
        if not text:
            raise HTTPException(status_code=400, detail="No data provided")
        
        graph_id = text.get('graphId')
        if not graph_id:
            raise HTTPException(status_code=400, detail="No graphId provided")
            
        inference_result = await infer(text.get('data'))
        evaluated_data = inference_result['data']

        with driver.session() as session:
            # First create all nodes
            for entity_type, entities in evaluated_data['entities'].items():
                # Convert snake_case to PascalCase for Neo4j labels
                label = ''.join(word.capitalize() for word in entity_type.rstrip('s').split('_'))
                
                # Create nodes for this entity type
                session.run(
                    f"""
                    UNWIND $entities as entity
                    MERGE (n:{label} {{name: CASE 
                        WHEN entity.title IS NOT NULL THEN entity.title 
                        ELSE entity.name 
                    END}})
                    """,
                    entities=entities
                )

            # Then create all relationships
            for rel in evaluated_data['relationships']:
                # Get the keys that aren't 'type'
                keys = [k for k in rel.keys() if k != 'type']
                source_key = keys[0]  # e.g., 'person'
                target_key = keys[1]  # e.g., 'organization'
                
                # Convert snake_case to PascalCase for labels
                source_label = ''.join(word.capitalize() for word in source_key.split('_'))
                target_label = ''.join(word.capitalize() for word in target_key.split('_'))
                
                session.run(
                    f"""
                    MATCH (source:{source_label} {{name: $source_value}})
                    MATCH (target:{target_label} {{name: $target_value}})
                    MERGE (source)-[r:{rel['type']}]->(target)
                    """,
                    {
                        'source_value': rel[source_key],
                        'target_value': rel[target_key]
                    }
                )

            # Store the raw data in InferenceData node
            result = session.run(
                """
                CREATE (n:InferenceData)
                SET n.id = $graph_id, n.data = $data
                RETURN n.id AS graphId
                """, 
                data=json.dumps(evaluated_data),
                graph_id=int(graph_id)
            ).single()
            
            if not result:
                raise HTTPException(status_code=404, detail="Failed to create graph")

        return ProcessResponse(
            status='success',
            graphId=str(graph_id)
        )

    except Exception as e:
        print(f"Error processing data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process/ontology")
async def process_ontology(request: Dict[str, Any]):
    try:
        graph_id = request.get('graphId')
        ontology_data = request.get('ontology')

        with driver.session() as session:
            # Get the stored data from Neo4j
            data_result = session.run(
                """
                MATCH (n:InferenceData)
                WHERE n.id = $graph_id
                RETURN n.data AS data
                """,
                graph_id=int(graph_id)
            ).single()
        
            if not data_result:
                raise HTTPException(status_code=404, detail="No data found for this graph")

            # Parse the Neo4j data
            stored_data = json.loads(data_result["data"])
            
            # Generate or use provided ontology
            if not ontology_data:
                ontology_data = await generate_ontology(stored_data)
            
            # Store the ontology back in Neo4j
            result = session.run(
                """
                MATCH (n:InferenceData)
                WHERE n.id = $graph_id
                SET n.ontology = $ontology
                RETURN n.data AS data, n.ontology AS ontology
                """,
                graph_id=int(graph_id),
                ontology=json.dumps(ontology_data)
            ).single()
            
            if not result:
                raise HTTPException(status_code=404, detail="Failed to store ontology")

            # Calculate metrics
            metrics = evaluate_all_metrics(
                response_json=stored_data,
                ontology_json=ontology_data
            )
            
            return {
                "status": "success",
                "message": "Ontology processed successfully",
                "entityResult": stored_data,
                "metrics": metrics
            }

    except Exception as e:
        print(f"Detailed error in process_ontology: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Query API endpoints
@app.post("/api/query/process_message")
async def process_message(request: Request):
    try:
        data = await request.json()
        current_message = data['currentMessage']
        conversation_history = data['conversationHistory']
        graph_id = data['graphId']
        graph_context = data.get('graphContext', {})
        
        print(f"Processing message for graph ID: {graph_id}")  # Debug log

        with driver.session() as session:
            result = session.run(
                """
                MATCH (n:InferenceData)
                WHERE n.id = $graph_id
                RETURN n.ontology AS ontology, n.data AS data
                """,
                graph_id=int(graph_id)
            ).single()

            if not result:
                raise HTTPException(status_code=404, detail=f"No data found for graph ID: {graph_id}")

            if not result["ontology"]:
                return StreamingResponse(
                    iter([f"data: {json.dumps({'content': 'Please upload an ontology first.'})}\n\n"]),
                    media_type='text/event-stream'
                )
            
            try:
                ontology_json = json.loads(result["ontology"])
                ontology = ontology_json["ontology"]  # Get the nested ontology object
                assert isinstance(ontology, dict), "Ontology must be a dictionary"
                assert "entities" in ontology, "Ontology must contain 'entities'"
                assert "relationships" in ontology, "Ontology must contain 'relationships'"
                
                graph_context["ontology"] = ontology
            except json.JSONDecodeError as e:
                print(f"Failed to parse ontology JSON: {e}")
                print(f"Raw ontology data: {result['ontology']}")
                raise

        async def generate():
            try:
                is_query_message = await is_query(current_message)
                print(f"Query classification result: {is_query_message}")
                
                query = is_query_message.get("query_engine", False)
                if query:
                    formatted_context = {
                        'nodes': [dict(node) for node in graph_context.get('nodes', [])],
                        'relationships': [dict(rel) for rel in graph_context.get('relationships', [])],
                        'ontology': graph_context.get('ontology', {})
                    }
                    result = await process_query(
                        message=current_message,
                        graph_context=formatted_context
                    )
                    
                    if result.get('error'):
                        error_message = {'content': f'Error: {result["error"]}'}
                        yield f"data: {json.dumps(error_message)}\n\n"
                        return
                        
                    if not result.get('response'):
                        yield f"data: {json.dumps({'content': 'No results found for your query.'})}\n\n"
                        return
                        
                    # Stream the response word by word
                    response_text = str(result['response']) # Convert to string in case it's not
                    words = response_text.split()
                    for word in words:
                        yield f"data: {json.dumps({'content': word + ' '})}\n\n"
                else:
                    async for chunk in process_conversation_with_llm(conversation_history):
                        yield f"data: {json.dumps({'content': chunk})}\n\n"
                    
                    yield "data: [DONE]\n\n"
                
            except Exception as e:
                print(f"Error in generate(): {str(e)}")
                yield f"data: {json.dumps({'content': f'An error occurred: {str(e)}'})}\n\n"

        return StreamingResponse(
            generate(), 
            media_type='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
            }
        )

    except Exception as e:
        print(f"Error in process_message: {str(e)}")
        return StreamingResponse(
            iter([f"data: {json.dumps({'content': f'An error occurred: {str(e)}'})}\n\n"]),
            media_type='text/event-stream'
        )

async def process_query(message: str, graph_context: Dict) -> Dict[str, Any]:
    try:
        result = await execute_llama_pipeline(message, graph_context)
        
        if not result:
            return {
                "error": "Query processor failed to generate valid results",
                "response": [],
                "relatedNodes": [],
                "graphContext": graph_context
            }
        
        # Format the response if it's a list of dictionaries
        if isinstance(result.get("response"), list) and result["response"]:
            try:
                # Extract values from nested dictionaries
                values = []
                for item in result["response"]:
                    # Handle nested dictionary structure (e.g., {'p': {'name': 'Uma Patel'}})
                    for key, value in item.items():
                        if isinstance(value, dict) and 'name' in value:
                            values.append(value['name'])
                        elif isinstance(value, str):
                            values.append(value)
                
                if len(values) > 1:
                    formatted_response = f"{', '.join(values[:-1])} and {values[-1]}"
                else:
                    formatted_response = values[0] if values else "No results found"
                    
                result["response"] = formatted_response
            except (IndexError, KeyError, AttributeError) as e:
                print(f"Error formatting response: {str(e)}")
                # If formatting fails, keep original response
                pass
        
        return {
            "response": result["response"],
            "query": result["query"],
            "source": "llama",
            "relatedNodes": [],
            "graphContext": graph_context
        }
        
    except Exception as e:
        print(f"Error in process_query: {str(e)}")
        return {
            "error": f"Query processing failed: {str(e)}",
            "response": [],
            "relatedNodes": [],
            "graphContext": graph_context
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000) 