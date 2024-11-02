import pandas as pd 
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['your_database']
collection = db['your_collection']

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Accept"]
    }
})
@app.route('/api/process-graph', methods=['POST'])
def process_graph():
    try:
        data = request.json.get('data')
        name = request.json.get('name')

        if not data: 
            return jsonify({'error': 'No data provided'}), 400
        
        # Put through the processing pipeline 
        # processed_data = process_data(data)

        result = collection.insert_one({
            'name': name, 
            'data': data
            # Add other fields as needed
        })

        return jsonify({'status': 'success', 'id': str(result.inserted_id)})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/api/process-ontology', methods=['POST'])
def process_ontology():
    try:
        name = request.json.get('name')
        ontology = request.json.get('ontology')

        if not name or not ontology:
            return jsonify({'error': 'Missing name or ontology'}), 400
        
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/graphs/<graph_id>', methods=['GET'])
def get_graph(name):
    try:
        # Fetch graph data from MongoDB using the ID
        graph = collection.find_one({"name": name})
        if not graph:
            return jsonify({'error': 'Graph not found'}), 404
        return jsonify({'entityResult': graph})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/process-data', methods=['POST', 'OPTIONS'])
def process_data():
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = request.json.get('data')
        ontology = request.json.get('ontology')
        name = request.json.get('name')
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # Process your data...
        # Save to MongoDB
        result = collection.insert_one({
            'name': name, 
            'data': data,
            'ontology': ontology
            # Add other fields as needed
        })
        
        return jsonify({
            'id': str(result.inserted_id),
            'entityResult': processed_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
