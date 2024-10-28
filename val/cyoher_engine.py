from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

# Load the CSV file (you can replace the path with the actual location on your system)
csv_file_path = r"C:\Users\valer\Desktop\inspected_test_graph.csv"  # Update with your local file path
graph_data = pd.read_csv(csv_file_path)

# Generate a Cypher query based on input and dataset
def generate_cypher_query(head_node, relationship, tail_node):
    # Convert all values to lowercase for case-insensitive comparison
    row = graph_data[(graph_data['head_node'].str.lower() == head_node.lower()) & 
                     (graph_data['relationship'].str.lower() == relationship.lower()) & 
                     (graph_data['tail_node'].str.lower() == tail_node.lower())]

    if not row.empty:
        # Generate a Cypher query if the relationship is found
        return f"MATCH (h:Entity {{name: '{head_node}'}})-[:{relationship.upper()}]->(t:Entity {{name: '{tail_node}'}}) RETURN h, t"
    else:
        return None

# Convert a Cypher query to natural language based on the dataset
def cypher_to_natural_language(head_node, relationship, tail_node):
    # Convert the relationship to natural language
    row = graph_data[(graph_data['head_node'].str.lower() == head_node.lower()) & 
                     (graph_data['relationship'].str.lower() == relationship.lower()) & 
                     (graph_data['tail_node'].str.lower() == tail_node.lower())]
    
    if not row.empty:
        # Construct a natural language sentence
        return f"{head_node} {relationship.lower()} {tail_node}."
    else:
        return "No matching relationship found in the dataset."

# Route to generate Cypher query and return the natural language relationship
@app.route('/generate_and_interpret_cypher', methods=['POST'])
def generate_and_interpret_cypher():
    data = request.get_json()

    # Extract head_node, relationship, and tail_node from the request data
    head_node = data.get("head_node")
    relationship = data.get("relationship")
    tail_node = data.get("tail_node")

    if not head_node or not relationship or not tail_node:
        return jsonify({"error": "head_node, relationship, and tail_node are required"}), 400

    # Generate Cypher query
    cypher_query = generate_cypher_query(head_node, relationship, tail_node)

    if cypher_query:
        # Convert Cypher to natural language
        natural_language = cypher_to_natural_language(head_node, relationship, tail_node)
        return jsonify({
            "cypher_query": cypher_query,
            "natural_language_relationship": natural_language
        }), 200
    else:
        return jsonify({"error": "No matching relationship found in the dataset"}), 404

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
