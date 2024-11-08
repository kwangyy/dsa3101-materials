import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn
from neo4j import GraphDatabase

# Load environment variables
load_dotenv()
api_key = os.getenv("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")
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
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "Valerie555%%%")
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

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

@app.post("/api/process-data", response_model=ProcessResponse)
async def process_data(text: Dict[str, Any]):
    try:
        print(f"Received text: {text}")

        if not text:
            raise HTTPException(status_code=400, detail="No data provided")
        
        # Placeholder for inference logic
        evaluated_data = infer(text)['data']

        # Store data in Neo4j
        with driver.session() as session:
            result = session.write_transaction(
                lambda tx: tx.run(
                    """
                    CREATE (n:InferenceData {data: $data})
                    RETURN id(n) AS graphId
                    """, data=evaluated_data
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

@app.post("/api/process-ontology", response_model=OntologyResponse)
async def process_ontology(data: OntologyRequest):
    try:
        print("Received request data:", data)

        # Retrieve data from Neo4j
        with driver.session() as session:
            result = session.read_transaction(
                lambda tx: tx.run(
                    """
                    MATCH (n:InferenceData)
                    WHERE id(n) = $graphId
                    RETURN n.data AS data
                    """, graphId=int(data.graphId)
                ).single()
            )

        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Document not found for graphId: {data.graphId}"
            )

        stored_data = result["data"]

        if not isinstance(stored_data, dict):
            raise HTTPException(
                status_code=500,
                detail="Stored data is not in the expected format"
            )

        # Placeholder for ontology evaluation logic
        metrics = evaluate_all_metrics(stored_data, {"ontology": data.ontology})
        
        return OntologyResponse(
            metrics=metrics,
            entityResult=stored_data
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Detailed error in process_ontology: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
