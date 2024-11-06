import json

# Load the JSON data
with open("C:/Users/valer/Desktop/data.json", "r") as f:
    data = json.load(f)["data"]

# Open a file to save Cypher commands
with open("C:/Users/valer/Desktop/generated_commands.cypher", "w") as cypher_file:
    # Create Person nodes
    for person in data['entities']['persons']:
        cypher_file.write(f"MERGE (p:Person {{name: '{person['name']}'}})\n")

    # Create Organization nodes
    for org in data['entities']['organizations']:
        cypher_file.write(f"MERGE (o:Organization {{name: '{org['name']}'}})\n")

    # Create Role nodes
    for role in data['entities']['roles']:
        cypher_file.write(f"MERGE (r:Role {{title: '{role['title']}'}})\n")

    # Create ProductService nodes
    for service in data['entities']['products_services']:
        cypher_file.write(f"MERGE (ps:ProductService {{name: '{service['name']}'}})\n")

    # Create Location nodes
    for location in data['entities']['locations']:
        cypher_file.write(f"MERGE (l:Location {{name: '{location['name']}'}})\n")

    # Create relationships
    for rel in data['relationships']:
        if rel['type'] == "AFFILIATED_WITH":
            cypher_file.write(
                f"MATCH (p:Person {{name: '{rel['person']}'}}), (o:Organization {{name: '{rel['organization']}'}})\n"
                f"MERGE (p)-[:AFFILIATED_WITH]->(o)\n"
            )
        elif rel['type'] == "HAS_ROLE":
            cypher_file.write(
                f"MATCH (p:Person {{name: '{rel['person']}'}}), (r:Role {{title: '{rel['role']}'}})\n"
                f"MERGE (p)-[:HAS_ROLE]->(r)\n"
            )
        elif rel['type'] == "INVOLVED_WITH":
            cypher_file.write(
                f"MATCH (p:Person {{name: '{rel['person']}'}}), (ps:ProductService {{name: '{rel['product_service']}'}})\n"
                f"MERGE (p)-[:INVOLVED_WITH]->(ps)\n"
            )
        elif rel['type'] == "LOCATED_AT":
            cypher_file.write(
                f"MATCH (o:Organization {{name: '{rel['organization']}'}}), (l:Location {{name: '{rel['location']}'}})\n"
                f"MERGE (o)-[:LOCATED_AT]->(l)\n"
            )

print("Cypher commands saved to generated_commands.cypher")

from neo4j import GraphDatabase

# Configure Neo4j connection
NEO4J_URI = "bolt://localhost:7687"  # Replace with your Neo4j instance URI
NEO4J_USER = "neo4j"                 # Replace with your Neo4j username
NEO4J_PASSWORD = "valerie555%%%"     # Replace with your Neo4j password

# Initialize Neo4j driver
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def execute_cypher_from_file(file_path):
    with driver.session() as session:
        with open(file_path, "r") as f:
            commands = f.read().splitlines()
            for command in commands:
                if command.strip():  # Ensure command is not empty
                    session.run(command)

# Path to the Cypher commands file
file_path = "C:/Users/valer/Desktop/generated_commands.cypher"
execute_cypher_from_file(file_path)

print("Cypher commands executed successfully.")

# Close the Neo4j driver connection
driver.close()
