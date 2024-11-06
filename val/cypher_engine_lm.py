from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize Neo4j driver
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

app = FastAPI()

# Define input model for Cypher query requests
class CypherQueryRequest(BaseModel):
    query: str

# Function to execute Cypher query on Neo4j
def execute_cypher_query(cypher_query):
    with driver.session() as session:
        result = session.run(cypher_query)
        # Convert result to a list of dictionaries for JSON-friendly output
        return [record.data() for record in result]

# API endpoint to process direct Cypher queries
@app.post("/cypher-query/")
async def process_cypher_query(request: CypherQueryRequest):
    try:
        # Execute the Cypher query on Neo4j
        response = execute_cypher_query(request.query)
        return {"response": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Ensure Neo4j driver is closed properly when the API shuts down
@app.on_event("shutdown")
async def shutdown_event():
    driver.close()
