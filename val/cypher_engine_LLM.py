from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from openai import OpenAI
import re

# Load the dataset (replace with the actual path)
dataset = pd.read_csv(r"C:\Users\valer\Desktop\inspected_test_graph.csv")

# Set your OpenAI API key
client = OpenAI()

# Initialize the FastAPI app
app = FastAPI()

# Define the request body model
class CypherQueryRequest(BaseModel):
    cypher_query: str

# Function to process a generalized Cypher-like query
def execute_cypher_query(cypher_query: str):
    """
    This function simulates a generalized Cypher query execution by searching the dataset.
    It parses the Cypher query to identify relationships between nodes and applies filters if present.
    """
    # Regular expression to capture the basic structure of a Cypher query
    match_pattern = r"MATCH \((?P<head_node>\w+):(?P<head_label>\w+)\)-\[(?P<relationship>:\w+)\]->\((?P<tail_node>\w+):(?P<tail_label>\w+)\)"
    condition_pattern = r"WHERE (?P<condition>.+)"

    # Extract the core match clause from the query
    match_result = re.search(match_pattern, cypher_query)
    if not match_result:
        return "Invalid or unsupported Cypher query."

    # Extract information from the Cypher query
    head_node = match_result.group("head_node")
    relationship = match_result.group("relationship").strip(":")
    tail_node = match_result.group("tail_node")

    # Check for a WHERE condition (optional)
    condition_result = re.search(condition_pattern, cypher_query)
    condition = None
    if condition_result:
        condition = condition_result.group("condition")

    # Build the dynamic query based on the extracted relationship and condition
    filtered_dataset = dataset[dataset['relationship'] == relationship]

    # Apply the condition if one is present (e.g., c.name = 'AI 101')
    if condition:
        key, value = condition.split('=')
        key = key.strip()
        value = value.strip().strip("'")  # Remove any extra quotes around the value
        if key == f"{tail_node}.name":  # Tail node condition
            filtered_dataset = filtered_dataset[filtered_dataset['tail_node'] == value]
        elif key == f"{head_node}.name":  # Head node condition
            filtered_dataset = filtered_dataset[filtered_dataset['head_node'] == value]

    # If we have matching data, construct a response
    if not filtered_dataset.empty:
        responses = []
        for _, row in filtered_dataset.iterrows():
            responses.append(f"{row['head_node']} {row['relationship']} {row['tail_node']}")
        return "; ".join(responses)

    return "No match found or unsupported query."


# API Endpoint for handling Cypher queries
@app.post("/query")
async def handle_cypher_query(request: CypherQueryRequest):
    """
    This API endpoint takes in a Cypher query and returns a natural language response.
    """
    cypher_query = request.cypher_query
    
    # Step 1: Execute the Cypher query on the dataset
    result = execute_cypher_query(cypher_query)

    # Step 2: Convert the result into natural language using GPT
    prompt = f"Convert the following result into natural language: '{result}'"


    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": "Write a haiku about recursion in programming."
            }
        ]
    )
    
    natural_language_output = response.choices[0].text.strip()
    
    # Return the natural language output
    # return {"natural_language_output": natural_language_output}
    return "True"

# To run the FastAPI server:
# Open a terminal and run `uvicorn main:app --reload`
