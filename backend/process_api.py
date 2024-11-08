import os 
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from bson import ObjectId
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn

# Local imports 
from llms.inference_model import infer
from ontology.ontology_evaluation import evaluate_all_metrics

# MongoDB setup
mongo_client = MongoClient('mongodb://localhost:27017/')
db = mongo_client['dsa3101']
collection = db['inference_data']

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
        
        evaluated_data = infer(text)['data']
        
        # Create new document
        result = collection.insert_one({
            'data': evaluated_data
        })

        return ProcessResponse(
            status='success',
            graphId=str(result.inserted_id)
        )
        
    except Exception as e:
        print(f"Error processing data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process-ontology", response_model=OntologyResponse)
async def process_ontology(data: OntologyRequest):
    try:
        print("Received request data:", data)

        try:
            object_id = ObjectId(data.graphId)
            stored_data = collection.find_one({"_id": object_id})
            print(f"Stored data: {stored_data}")

        except Exception as e:
            print(f"MongoDB error: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid graphId format")

        if not stored_data:
            raise HTTPException(
                status_code=404, 
                detail=f"Document not found for graphId: {data.graphId}"
            )

        if not isinstance(stored_data, dict):
            raise HTTPException(
                status_code=500, 
                detail="Stored data is not in the expected format"
            )

        metrics = evaluate_all_metrics(stored_data, {"ontology": data.ontology})
        
        return OntologyResponse(
            metrics=metrics,
            entityResult=stored_data.get('data', {})
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Detailed error in process_ontology: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
