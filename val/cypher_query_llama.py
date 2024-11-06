from huggingface_hub import InferenceClient
import json

# Load the data from JSON file
def load_data(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)['data']
    return data

# Prepare a specific prompt for finding the organization affiliation of a person
def prepare_prompt_for_affiliation(data, person_name):
    # Check if the specified person has any affiliation with an organization
    affiliated_with = [rel['organization'] for rel in data['relationships'] if rel['type'] == "AFFILIATED_WITH" and rel['person'] == person_name]
    
    if affiliated_with:
        # If affiliation exists, create a specific prompt
        prompt = f"What organization is {person_name} in? Generate a Cypher query to find the organization affiliated with {person_name}."
    else:
        # If no affiliation is found, inform that no data is available
        prompt = f"There is no affiliation information for {person_name} in the data."
    
    return prompt

# Initialize Hugging Face client
client = InferenceClient(api_key="")

# Load data from JSON file at the specified path
data = load_data(r"C:\Users\valer\Desktop\data.json")

# Specify the person for whom you want to generate the Cypher query
person_name = "Uma Patel"
prompt = prepare_prompt_for_affiliation(data, person_name)

# Prepare the message for the model
messages = [
    {
        "role": "user",
        "content": prompt
    }
]

# Generate Cypher query using the model with non-streamed output to avoid truncation
response = client.chat.completions.create(
    model="meta-llama/Llama-3.1-8B-Instruct", 
    messages=messages, 
    max_tokens=500,
    stream=False
)

# Collect the generated Cypher query
generated_query = response.choices[0].message.content
print("Generated Cypher Query:", generated_query)

# Save the generated query to a file
output_file_path = r"C:\Users\valer\Desktop\generated_cypher_query.txt"
with open(output_file_path, "w") as file:
    file.write(generated_query)

print(f"Generated Cypher query saved to {output_file_path}")
