import pandas as pd 
from flask import Flask, request, jsonify
from flask_cors import CORS

df = pd.read_csv('test_graph.csv')
test = df.to_dict(orient='records')

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Accept"]
    }
})

@app.route('/api/process-data', methods=['POST', 'OPTIONS'])
def process_data():
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        print("Received request")
        print("Request data:", request.json)
        
        data = request.json.get('data')
        ontology = request.json.get('ontology')
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        print(test)
        return jsonify({'entityResult': test})
        
        # # Process the text data into a graph structure
        # lines = data.strip().split('\n')
        # nodes = set()
        # links = []
        
        # for line in lines:
        #     if ',' in line:
        #         source, target = map(str.strip, line.split(','))
        #         nodes.add(source)
        #         nodes.add(target)
        #         links.append({"source": source, "target": target})
        
        # result = {
        #     "nodes": [{"id": node} for node in nodes],
        #     "links": links
        # }
    except Exception as e:
        print("Error:", str(e))
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
