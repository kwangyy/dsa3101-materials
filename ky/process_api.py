import pandas as pd 
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from ontology_evaluation import evaluate_all_metrics
from bson.objectid import ObjectId

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['email']
collection = db['email_ground_truth_prediction']

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
        data = request.json.get('data')

        if not data: 
            return jsonify({'error': 'No data provided'}), 400
        
        # Create new document
        result = collection.insert_one({
            'data': data,
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
            stored_data = collection.find_one({"name": "test"})
            print(stored_data)

        except Exception as e:
            print(f"MongoDB error: {str(e)}")
            return jsonify({'error': 'Invalid graphId format'}), 400

        if not stored_data:
            return jsonify({'error': f'Document not found for graphId: {graph_id}'}), 404

        metrics = evaluate_all_metrics(stored_data, {"ontology": ontology})
        
        return jsonify({
            'metrics': metrics,
            'entityResult': stored_data['data']
        })
        
    except Exception as e:
        print(f"Detailed error in process_ontology: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
