# Knowledge Graph Backend

A FastAPI-based backend service for processing text data, generating ontologies, and managing a knowledge graph using Neo4j.

## Features

- Text processing and entity extraction
- Ontology generation and management
- Knowledge graph creation and querying
- Conversation handling with LLM integration
- Real-time streaming responses
- Neo4j database integration

## Prerequisites

- Python 3.8+
- Neo4j Database
- Hugging Face API Token

## Installation

1. Clone the repository
2. Install dependencies:
```
pip install -r requirements.txt
```

## Environment Setup

Create a `.env` file in the root directory with the following variables:

```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
HUGGINGFACE_API_KEY=your_huggingface_api_key
``` 

## Core Components

### API Endpoints

The main API endpoints are defined in `api.py`:

1. `/api/process/data` - Process text data and create graph nodes
2. `/api/process/ontology` - Process and evaluate ontologies
3. `/api/query/process_message` - Handle user queries and conversations

### LLM Models

The system uses several specialized LLM models:

1. **Inference Model**: Extracts entities and relationships from text
2. **Ontology Model**: Generates and manages ontology structures
3. **Query Model**: Classifies and processes user queries
4. **Conversation Model**: Handles natural language conversations

### Database Integration

Neo4j is used as the graph database, with integration handled through `cypher_engine.py`. The system supports:

- Node creation and relationship management
- Query execution
- Data persistence

## Usage

1. Start the server:

```
uvicorn api:app --reload
``` 

2. The API will be available at `http://localhost:5000`

3. Frontend can connect to `http://localhost:5000/api/xxxx`, where xxxx is the endpoint name.
