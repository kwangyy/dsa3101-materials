import os
from dotenv import load_dotenv
from llms.llm_utils import create_llm_client, process_with_llm
import asyncio

load_dotenv()

is_query_prompt = """You are an expert at differentiating queries from text. You are currently working on an enterprise knowledge graph, and you are given a query from a user.


Your task is to differentiate if a query is a question that requires the query engine provided to you or not. 
Examples of questions that do not require the query engine are questions that do not require any specific data from the graph.
Do not justify your answer. Do not output anything else, except the JSON object.
If the query is a question that requires the query engine, output the JSON object {{"query_engine": true}}.
If the query is not a question that requires the query engine, output the JSON object {{"query_engine": false}}.

Some examples have been provided below:
Question: What is the relationship between IBM and Uma Patel?
Query Engine: True

Question: This is not what I want.
Query Engine: False

Question: What is the weather in Tokyo like?
Query Engine: False

The query has been provided below:
{currentMessage}
"""

async def is_query(input_json):
    client = create_llm_client("meta-llama/Llama-3.1-8B-Instruct", os.getenv("HF_TOKEN"))
    if isinstance(input_json, str):
        input_json = {"currentMessage": input_json}
    elif isinstance(input_json, dict) and "currentMessage" not in input_json:
        input_json = {"currentMessage": str(input_json)}
    
    return await process_with_llm(client, input_json, is_query_prompt, input_key="currentMessage")

if __name__ == "__main__":
    async def test_query():
        json_response = await is_query({"currentMessage": "What is the capital of France?"})
        print(json_response)
    
    asyncio.run(test_query())
