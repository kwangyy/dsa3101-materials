import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List 
import uvicorn
from neo4j import GraphDatabase
import asyncio
import json
# Local imports 
from llms.inference_model import infer
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

@app.post("/api/process-data", response_model=ProcessResponse)
async def process_data(text: Dict[str, Any]):
    try:
        if not text:
            raise HTTPException(status_code=400, detail="No data provided")
        
        inference_result = await infer(text)
        evaluated_data = inference_result['data']
        
        # Serialize the complex data structure to JSON string
        serialized_data = json.dumps(evaluated_data)

        with driver.session() as session:
            result = session.execute_write(
                lambda tx: tx.run(
                    """
                    CREATE (n:InferenceData {data: $data})
                    RETURN id(n) AS graphId
                    """, 
                    data=serialized_data  # Pass the serialized JSON string
                ).single()
            )
            graph_id = result["graphId"]

        return ProcessResponse(
            status='success',
            graphId=str(graph_id)
        )

    except Exception as e:
        print(f"Error processing data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process-ontology")
async def process_ontology(request: Dict[str, Any]):
    try:
        print(f"Received request data: graphId='{request.get('graphId')}' ontology={request.get('ontology')}")
        
        # Extract data from request
        graph_id = request.get('graphId')
        ontology_data = request.get('ontology')
        
        with driver.session() as session:
            # First get the stored data
            result = session.run(
                """
                MATCH (n:InferenceData) 
                WHERE id(n) = $graph_id
                RETURN n.data AS data
                """,
                graph_id=int(graph_id)
            ).single()
            
            if not result:
                raise HTTPException(status_code=404, detail="Graph not found")
            
            # Parse the stored JSON string back into a dictionary
            stored_data = json.loads(result["data"])
            
            # Store the ontology
            serialized_ontology = json.dumps(ontology_data)
            session.run(
                """
                MATCH (n:InferenceData) 
                WHERE id(n) = $graph_id
                SET n.ontology = $ontology
                """,
                graph_id=int(graph_id),
                ontology=serialized_ontology
            )
            
        return {
            "status": "success",
            "message": "Ontology processed successfully",
            "entityResult": stored_data
        }

    except Exception as e:
        print(f"Detailed error in process_ontology: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
