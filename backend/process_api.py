import pandas as pd 
import os 
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from ontology_evaluation import evaluate_all_metrics
from inference_model import eval_json_input
from bson import ObjectId

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['dsa3101']
collection = db['inference_data']

load_dotenv()
api_key = os.getenv("HF_TOKEN")
client = InferenceClient("meta-llama/Llama-3.1-8B-Instruct", api_key=api_key)

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Accept"]
    }
})
@app.route('/api/process-data', methods=['POST'])
def process_data():
    try:
        text = request.json
        print(f"Received text: {text}")

        if not text: 
            return jsonify({'error': 'No data provided'}), 400
        
        evaluated_data = eval_json_input(text, client)['data']
        
        # Create new document
        result = collection.insert_one({
            'data': evaluated_data
        })

        return jsonify({
            'status': 'success',
            'graphId': str(result.inserted_id),  
        })
        
    except Exception as e:
        print(f"Error processing data: {str(e)}")
        return jsonify({'error': str(e)}), 500
    

@app.route('/api/process-ontology', methods=['POST'])
def process_ontology():
    try:
        data = request.json
        print("Received request data:", data)
        
        graph_id = data.get('graphId')
        ontology = data.get('ontology')

        if not graph_id:
            return jsonify({'error': 'Missing graphId'}), 400
            
        if not ontology:
            return jsonify({'error': 'Missing ontology data'}), 400

        try:
            object_id = ObjectId(graph_id)
            stored_data = collection.find_one({"_id": object_id})
            print(f"Stored data: {stored_data}")

        except Exception as e:
            print(f"MongoDB error: {str(e)}")
            return jsonify({'error': 'Invalid graphId format'}), 400

        if not stored_data:
            return jsonify({'error': f'Document not found for graphId: {graph_id}'}), 404

        if not isinstance(stored_data, dict):
            return jsonify({'error': 'Stored data is not in the expected format'}), 500

        metrics = evaluate_all_metrics(stored_data, {"ontology": ontology})
        
        return jsonify({
            'metrics': metrics,
            'entityResult': stored_data.get('data', {})
        })
        
    except Exception as e:
        print(f"Detailed error in process_ontology: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
