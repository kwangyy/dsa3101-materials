# Standard library imports
from typing import List, Dict, Any
import asyncio
from typing import Optional

# Third-party imports
from fastapi import FastAPI
import uvicorn

# Local imports 
from llms.query_model import is_query
from llms.conversation_model import process_conversation_with_llm
from query.nl2cql_query import generate_cypher
from query.cypher_engine import execute_cypher_query
from query.llama_query import query_generator

# Initialize FastAPI
app = FastAPI()

# Helper functions
def format_conversation_for_llm(conversation_history: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Format conversation history for LLM input."""
    formatted_messages = []
    
    formatted_messages.append({
        "role": "system",
        "content": "You are a helpful assistant with knowledge about the graph database."
    })
    
    for message in conversation_history:
        role = "system" if message["role"] == "assistant" else message["role"]
        formatted_messages.append({
            "role": role,
            "content": message["content"]
        })
    
    return formatted_messages

async def execute_nl2cql_pipeline(message: str) -> Optional[Dict[str, Any]]:
    """Execute the NL2CQL pipeline."""
    try:
        cypher_result = generate_cypher({"prompt": message})
        if "error" in cypher_result:
            return None
            
        query_result = execute_cypher_query(cypher_result["cypher_query"])
        return {
            "response": query_result,
            "query": cypher_result["cypher_query"],
            "source": "nl2cql"
        }
    except Exception as e:
        print(f"NL2CQL pipeline error: {str(e)}")
        return None

async def execute_llama_pipeline(message: str, graph_context: Dict) -> Optional[Dict[str, Any]]:
    """Execute the LLaMA pipeline."""
    try:
        cypher_query = await query_generator(message, graph_context.get("ontology", ""))
        if not cypher_query:
            return None
            
        query_result = execute_cypher_query(cypher_query)
        return {
            "response": query_result,
            "query": cypher_query,
            "source": "llama"
        }
    except Exception as e:
        print(f"LLaMA pipeline error: {str(e)}")
        return None

# API Endpoints
@app.post("/process_message")
async def process_message(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process chat messages and return response."""
    try:
        current_message = data['currentMessage']
        conversation_history = data['conversationHistory']
        graph_id = data['graphId']
        graph_context = data.get('graphContext', {})

        is_query_message = await is_query(current_message)
        
        if is_query_message:
            result = await process_query(
                message=current_message,
                graph_id=graph_id,
                graph_context=graph_context
            )
            return {
                'response': result['response'],
                'type': 'query',
                'relatedNodes': result.get('relatedNodes', []),
                'graphContext': result.get('graphContext', {})
            }
        else:
            formatted_messages = format_conversation_for_llm(conversation_history)
            result = await process_conversation_with_llm(formatted_messages)
            return {
                'response': result['response'],
                'type': 'conversation'
            }

    except Exception as e:
        return {"error": str(e)}

@app.post("/process_query")
async def process_query(message: str, graph_context: Dict) -> Dict[str, Any]:
    """Handle processing for messages classified as queries using both NL2CQL and LLaMA pipelines concurrently."""
    nl2cql_task = asyncio.create_task(execute_nl2cql_pipeline(message))
    llama_task = asyncio.create_task(execute_llama_pipeline(message, graph_context))
    
    done, pending = await asyncio.wait(
        {nl2cql_task, llama_task},
        return_when=asyncio.FIRST_COMPLETED
    )
    
    first_result = done.pop().result()
    
    if first_result and first_result["source"] == "nl2cql":
        for task in pending:
            task.cancel()
        return {
            "response": first_result["response"],
            "query": first_result["query"],
            "source": "nl2cql",
            "relatedNodes": [],
            "graphContext": graph_context
        }
    
    try:
        if pending:
            second_result = await pending.pop()
            if second_result:
                first_result = second_result
    except asyncio.CancelledError:
        pass
    
    if not first_result:
        return {
            "error": "Both query processors failed to generate valid results",
            "response": [],
            "relatedNodes": [],
            "graphContext": graph_context
        }
    
    return {
        "response": first_result["response"],
        "query": first_result["query"],
        "source": first_result["source"],
        "relatedNodes": [],
        "graphContext": graph_context
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5001)
