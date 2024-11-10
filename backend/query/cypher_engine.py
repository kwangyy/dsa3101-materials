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

# Define input model for Cypher query requests
class CypherQueryRequest(BaseModel):
    query: str

# Function to execute Cypher query on Neo4j
def execute_cypher_query(cypher_query):
    with driver.session() as session:
        result = session.run(cypher_query)
        # Convert result to a list of dictionaries for JSON-friendly output
        return [record.data() for record in result]
    
if __name__ == "__main__":
    query = "MATCH (n) RETURN n"
    result = execute_cypher_query(query)
    print(result)

