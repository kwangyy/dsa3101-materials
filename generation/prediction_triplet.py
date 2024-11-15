import json
import os

# Directory containing JSON files - to modify for email threads
input_dir = "minutes_test" 
output_dir = "minutes_triplets_output"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Loop through each file in the directory
for filename in os.listdir(input_dir):
    # Only process files that match the "response_1_evaluated.json" pattern
    if filename.startswith("response_") and filename.endswith("_evaluated.json"):
        input_path = os.path.join(input_dir, filename)
        
        # Load the JSON data from the file
        with open(input_path, "r") as file:
            data = json.load(file)["data"]

        # Initialize a list to store triplets
        triplets = []

        # Process each relationship in the JSON
        for rel in data["relationships"]:
            triplet = {}
            
            # Mapping relationship details to triplet format
            if rel["type"] == "AFFILIATED_WITH":
                triplet = {
                    "person": rel["person"],
                    "organization": rel["organization"],
                    "relationship": "AFFILIATED_WITH"
                }
            elif rel["type"] == "HAS_ROLE":
                triplet = {
                    "person": rel["person"],
                    "role": rel["role"],
                    "relationship": "HAS_ROLE"
                }
            elif rel["type"] == "INVOLVED_WITH":
                triplet = {
                    "person": rel["person"],
                    "product_service": rel["product_service"],
                    "relationship": "INVOLVED_WITH"
                }
            elif rel["type"] == "LOCATED_AT":
                triplet = {
                    "organization": rel["organization"],
                    "location": rel["location"],
                    "relationship": "LOCATED_AT"
                }

            # Add the triplet to the list
            triplets.append(triplet)

        # Define the output file path, changing the file name to avoid overwriting
        output_filename = f"triplets_{filename}"
        output_path = os.path.join(output_dir, output_filename)

    # Save the triplets as a JSON array
    with open(output_path, "w") as output_file:
        json.dump(triplets, output_file, indent=4)

    print(f"Triplet conversion completed for {filename}, saved to {output_path}")