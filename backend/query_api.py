from llms.query_model import is_query
from llms.conversation_model import process_conversation_with_llm
from typing import Dict, Any, List
from datetime import datetime

async def process_message(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process chat messages and return response.
    """
    try:
        current_message = data['currentMessage']
        conversation_history = data['conversationHistory']
        graph_id = data['graphId']
        graph_context = data.get('graphContext', {})

        # Check if it's a query
        is_query_message = await is_query(current_message)
        
        if is_query_message:
            # Handle as graph query
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
            # Handle as conversation
            # Format conversation history for LLM
            formatted_messages = format_conversation_for_llm(conversation_history)
            result = await process_conversation_with_llm(formatted_messages)
            return {
                'response': result['response'],
                'type': 'conversation'
            }

    except Exception as e:
        return {"error": str(e)}

def format_conversation_for_llm(conversation_history: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Format conversation history for LLM input.
    """
    formatted_messages = []
    
    # Add system prompt if needed
    formatted_messages.append({
        "role": "system",
        "content": "You are a helpful assistant with knowledge about the graph database."
    })
    
    # Add conversation history
    for message in conversation_history:
        # Convert 'assistant' role to 'system' if needed by your LLM
        role = "system" if message["role"] == "assistant" else message["role"]
        formatted_messages.append({
            "role": role,
            "content": message["content"]
        })
    
    return formatted_messages

async def process_query(message: str, graph_id: str, graph_context: Dict) -> Dict[str, Any]:
    """
    Handle processing for messages classified as queries.
    """
    # Add your query processing logic here
    pass


