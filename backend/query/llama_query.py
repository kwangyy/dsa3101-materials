import os
import json
from dotenv import load_dotenv
from llms.llm_utils import create_llm_client, process_with_llm, process_files
import asyncio

load_dotenv()

llama_query_prompt = """You are a professional Neo4j Cypher Query writer. 
You are given a query as well as the ontology of the knowledge graph. 
Given this information, you are to write a Cypher query that will efficiently retrieve the related items without error. 
You are to assue that all of the items within the query are present, and use them as ground truth. 
Return the Cypher query as a string.

An example has been provided below:
Query: What are the names of the people who work at IBM?
Ontology: 
MATCH (p:Person)-[:WORKS_AT]->(o:Organization {name: 'IBM'})
RETURN p.name

The query is as follows:
{query}
The ontology is as follows:
{ontology}
"""

async def query_generator(query, ontology):
    formatted_input = {"query": query, "ontology": ontology}

    client = create_llm_client("meta-llama/Llama-3.1-8B-Instruct", os.getenv("HF_TOKEN"))
    return await process_with_llm(client, formatted_input, llama_query_prompt, input_key=["query", "ontology"])

if __name__ == "__main__":
    pass