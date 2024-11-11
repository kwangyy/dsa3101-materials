import os
import json
from dotenv import load_dotenv
from llms.llm_utils import create_llm_client, process_with_llm, process_files
import asyncio

load_dotenv()

llama_query_prompt = """You are a professional Neo4j Cypher Query writer. 
You are given a query as well as the ontology of the knowledge graph. 
Given this information, you are to write a Cypher query that will efficiently retrieve the related items without error. 
You are to assume that all of the items within the query are present, and use them as ground truth. 
You are also to assume that the relationships are as defined in the ontology. Do NOT make any assumptions about the relationships.
If there are more than two Cypher queries, determine the best one to use and return ONLY that Cypher Query, with no other text.
Return in JSON format, with the key "cypher_query" and the value as the Cypher Query.

An example has been provided below:
Query: What are the names of the people who work at IBM?
Ontology: 
{{"entities": [{{"type": "Person", "properties": {{"name": "string", "affiliated_with": ["Organization"], "roles": ["Role"], "involved_with": ["Product/Service"]}}, {{"type": "Organization", "properties": {{"name": "string", "located_at": "Location", "collaborates_with": ["Organization"]}}, {{"type": "Role", "properties": {{"name": "string", "assigned_to": ["Person"]}}, {{"type": "Product/Service", "properties": {{"name": "string", "involves_person": ["Person"]}}, {{"type": "Location", "properties": {{"name": "string", "organizations": ["Organization"]}}], "relationships": [{{"type": "AFFILIATED_WITH", "from": "Person", "to": "Organization"}}, {{"type": "HAS_ROLE", "from": "Person", "to": "Role"}}, {{"type": "INVOLVED_WITH", "from": "Person", "to": "Product/Service"}}, {{"type": "LOCATED_AT", "from": "Organization", "to": "Location"}}, {{"type": "COLLABORATION", "from": "Organization", "to": "Organization"}}]}}


{{"cypher_query": "MATCH (p:Person)-[:AFFILIATED_WITH]->(o:Organization {{name: 'IBM'}}) RETURN p.name"}}

The query is as follows:
{query}
The ontology is as follows:
{ontology}
"""

async def query_generator(query, ontology):
    formatted_input = {"query": query, "ontology": ontology}

    client = create_llm_client("meta-llama/Llama-3.1-70B-Instruct", os.getenv("HF_TOKEN"))
    cypher_query = await process_with_llm(client, formatted_input, llama_query_prompt, input_key=["query", "ontology"])
    print("Query:")
    print(cypher_query)
    return cypher_query

if __name__ == "__main__":
    pass