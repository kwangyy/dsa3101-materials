import os
from dotenv import load_dotenv
from llm_utils import create_llm_client, process_with_llm

load_dotenv()

query_prompt = """You are an expert at differentiating queries from text.

Your task is to differentiate if a query is a question that requires the query engine provided to you or not. 
If the query is a question that requires the query engine, output the JSON object {{"query_engine": true}}.
If the query is not a question that requires the query engine, output the JSON object {{"query_engine": false}}.

Some examples have been provided below:
Question: What is the capital of France?
Query Engine: True

Question: This is not what I want.
Query Engine: False

Question: What is the weather in Tokyo?
Query Engine: True

The query has been provided below:
{query}
"""

def is_query(input_json):
    client = create_llm_client("meta-llama/Llama-3.1-8B-Instruct", os.getenv("HF_TOKEN"))
    return process_with_llm(client, input_json, query_prompt, input_key="query")

if __name__ == "__main__":
    json_response = is_query({"query": "What is the capital of France?"})
    print(json_response)
