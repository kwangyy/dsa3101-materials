import os
import json
import re
from datetime import datetime
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from flask import jsonify

load_dotenv()
api_key = os.getenv("HF_TOKEN")

eval_prompt = """Your task is to extract entities, as well as define any relationships between them, outputting only a single JSON object for which the format MUST be adhered to, with no other text. The entity types to extract are:

Person/Organization
Role
Location (Try not to make too many assumptions)
Product/Service

The head-tail relationships (if present) to be extracted are:
Person-Organization "AFFILIATED_WITH"
Person-Role Association "HAS_ROLE"
Person-Product/Service "INVOLVED_WITH"
Organization-Location "LOCATED_AT"

The JSON has two main sections:

    Entities: Lists various categories such as people, organizations, roles, locations, and products/services, each containing attributes like name or title.

    Relationships: Defines the connections between entities, specifying types like AFFILIATED_WITH, HAS_ROLE, INVOLVED_WITH, and LOCATED_AT. Each relationship entry links entities by referencing their names (e.g., a person's affiliation with an organization, their role, or the location of an organization)

JSON Format with dummy examples:

{{  
  "data": {{  
    "entities": {{  
      "persons": [  
        {{  
          "name": "John Doe"  
        }}  
      ],  
      "organizations": [  
        {{  
          "name": "Acme Corp"  
        }}  
      ],  
      "roles": [  
        {{  
          "title": "CEO"  
        }}  
      ],  
      "locations": [  
        {{  
          "name": "New York"  
        }}  
      ],  
      "products_services": [  
        {{  
          "name": "Widget X"  
        }}  
      ]  
    }},  
    "relationships": [  
      {{  
        "type": "AFFILIATED_WITH",  
        "person": "John Doe",  
        "organization": "Acme Corp"  
      }},  
      {{  
        "type": "HAS_ROLE",  
        "person": "John Doe",  
        "role": "CEO"  
      }},  
      {{  
        "type": "INVOLVED_WITH",  
        "person": "John Doe",  
        "product_service": "Widget X"  
      }},  
      {{  
        "type": "LOCATED_AT",  
        "organization": "Acme Corp",  
        "location": "New York"  
      }}  
    ]  
  }}  
}}  

Do not include comments within the JSON.

TEXT:
{text}

"""

def extract_json_from_response(response_text):
    """
    Extracts JSON from response text, handling code blocks and multiline content.
    Removes comments before parsing.
    """
    def remove_comments(json_str):
        # Remove single-line comments
        json_str = re.sub(r'#.*$', '', json_str, flags=re.MULTILINE)
        json_str = re.sub(r'//.*$', '', json_str, flags=re.MULTILINE)
        # Remove multi-line comments
        json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
        return json_str

    # First try to find JSON within code blocks
    code_block_pattern = r'```json\s*([\s\S]*?)\s*```'
    code_block_match = re.search(code_block_pattern, response_text)
    
    if code_block_match:
        try:
            json_str = code_block_match.group(1)
            json_str = remove_comments(json_str)
            json_object = json.loads(json_str)
            return json_object
        except json.JSONDecodeError:
            pass

    # If no code block or invalid JSON, try general JSON pattern
    json_pattern = r'(?s)\{.*?\}(?=\s*$)'
    json_match = re.search(json_pattern, response_text)
    
    if json_match:
        json_str = json_match.group(0)
        json_str = remove_comments(json_str)
        try:
            json_object = json.loads(json_str)
            return json_object
        except json.JSONDecodeError:
            pass

    # Return None if no valid JSON is found
    return None


def eval_text_files(input_folder, output_folder, client):
    """
    Evaluates the content of .txt files in the input folder and writes the results to the output folder.
    Only processes files if the corresponding output file does not already exist.
    """
    # Check if the input folder exists
    if not os.path.exists(input_folder):
        print(f"The folder '{input_folder}' does not exist.")
        return

    # Check if the output folder exists, create it if it doesn't
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # List all files in the input folder
    files = os.listdir(input_folder)

    # Filter out only .txt files
    txt_files = [f for f in files if f.endswith('.txt')]

    # Evaluate the content of each .txt file
    for txt_file in txt_files:
        txt_file_path = os.path.join(input_folder, txt_file)
        base_name = os.path.splitext(txt_file)[0]
        evaluated_filename = f"{base_name}_evaluated.json"
        evaluated_file_path = os.path.join(output_folder, evaluated_filename)

        # Check if the evaluated file already exists
        if os.path.exists(evaluated_file_path):
            print(f"Skipping '{txt_file}' as '{evaluated_filename}' already exists.")
            continue

        # Read the content of the .txt file
        with open(txt_file_path, 'r') as file:
            text_content = file.read()

        populated_prompt = eval_prompt.format(
            text=text_content
        )
        print(f"evaluating {txt_file}...")
        completion = client.chat.completions.create(
            model="meta-llama/Llama-3.1-8B-Instruct", 
            messages=[ 
                {"role": "user", "content": populated_prompt}],
   
            temperature=0.8,
            max_tokens=4096,
            top_p=0.7,
            stream=False
            )
        response_text = completion.choices[0].message.content
        print(response_text)
        
        extracted_json = extract_json_from_response(response_text)
        base_name, _ = os.path.splitext(txt_file)
        evaluated_filename = f"{base_name}_evaluated.json"
        evaluated_file_path = os.path.join(output_folder, evaluated_filename)

        # Write the evaluated content to the output file
        with open(evaluated_file_path, 'w') as output_file:
            json.dump(extracted_json, output_file, indent=4)

        print(f"Evaluated '{txt_file}' and saved to '{evaluated_filename}'.")


def eval_json_input(input_json, client):
    """
    Evaluates the content from a JSON input and writes the results to a JSON file.
    
    Args:
        input_json (dict): A dictionary with structure {'data': 'text content'}
    
    Returns:
        str: Path to the output file
    """
    # Extract the text content from the input JSON
    if not isinstance(input_json, dict) or 'data' not in input_json:
        raise ValueError("Input JSON must be a dictionary with a 'data' key")
    
    text_content = input_json["data"]
    
    # Generate the populated prompt
    populated_prompt = eval_prompt.format(text=text_content)
    
    print("Evaluating JSON input...")
    # Make the API call
    completion = client.chat.completions.create(
        model="meta-llama/Llama-3.1-8B-Instruct",
        messages=[
            {"role": "user", "content": populated_prompt}
        ],
        temperature=0.8,
        max_tokens=4096,
        top_p=0.7,
        stream=False
    )
    response_text = completion.choices[0].message.content
    print(response_text)
    
    # Extract JSON from the response
    extracted_json = extract_json_from_response(response_text)
    
    print("Inference done")
    return extracted_json


if __name__ == "__main__":
    client = InferenceClient("meta-llama/Llama-3.1-8B-Instruct", api_key=api_key)
    
    with open("1.json", 'r') as file:
        json_obj = json.load(file)

    eval_json_input(json_obj, client)

# string = """{\n  \"entities\": {\n    \"persons\": [\n      {\n        \"name\": \"Tina Foster\"\n      },\n      {\n        \"name\": \"Quinn Parker\"\n      },\n      {\n        \"name\": \"Carol Nguyen\"\n      },\n      {\n        \"name\": \"Derek Hill\"\n      },\n      {\n        \"name\": \"Natalie Wu\"\n      }\n    ],\n    \"organizations\": [\n      {\n        \"name\": \"IBM\"\n      }\n    ],\n    \"roles\": [\n      {\n        \"title\": \"IT Support Specialist\"\n      },\n      {\n        \"title\": \"Data Analyst\"\n      },\n      {\n        \"title\": \"Junior Data Scientist\"\n      },\n      {\n        \"title\": \"QA Engineer\"\n      },\n      {\n        \"title\": \"Product Marketing Manager\"\n      }\n    ],\n    \"locations\": [\n      \n    ],\n    \"products_services\": [\n      {\n        \"name\": \"QRadar SIEM\"\n      },\n      {\n        \"name\": \"IBM Cognos Analytics\"\n      },\n      {\n        \"name\": \"Microsoft Azure\"\n      },\n      {\n        \"name\": \"Splunk\"\n      }\n    ]\n  },\n  \"relationships\": [\n    {\n      \"type\": \"AFFILIATED_WITH\",\n      \"person\": \"Tina Foster\",\n      \"organization\": \"IBM\"\n    },\n    {\n      \"type\": \"HAS_ROLE\",\n      \"person\": \"Tina Foster\",\n      \"role\": \"IT Support Specialist\"\n    },\n    {\n      \"type\": \"INVOLVED_WITH\",\n      \"person\": \"Quinn Parker\",\n      \"product_service\": \"QRadar SIEM\"\n    },\n    {\n      \"type\": \"LOCATED_AT\",\n      \"organization\": \"IBM\",\n      \"location\": \"\"\n    },\n    {\n      \"type\": \"HAS_ROLE\",\n      \"person\": \"Quinn Parker\",\n      \"role\": \"Data Analyst\"\n    },\n    {\n      \"type\": \"AFFILIATED_WITH\",\n      \"person\": \"Carol Nguyen\",\n      \"organization\": \"IBM\"\n    },\n    {\n      \"type\": \"HAS_ROLE\",\n      \"person\": \"Carol Nguyen\",\n      \"role\": \"Junior Data Scientist\"\n    },\n    {\n      \"type\": \"INVOLVED_WITH\",\n      \"person\": \"Carol Nguyen\",\n      \"product_service\": \"Microsoft Azure\"\n    },\n    {\n      \"type\": \"AFFILIATED_WITH\",\n      \"person\": \"Derek Hill\",\n      \"organization\": \"IBM\"\n    },\n    {\n      \"type\": \"HAS_ROLE\",\n      \"person\": \"Derek Hill\",\n      \"role\": \"QA Engineer\"\n    },\n    {\n      \"type\": \"INVOLVED_WITH\",\n      \"person\": \"Natalie Wu\",\n      \"product_service\": \"Splunk\"\n    }\n  ]\n}"""
# print(extract_json_from_response(string))

#
# completion = client.chat.completions.create(
#             model="meta-llama/Llama-3.1-8B-Instruct", 
#             messages=[ 
#                 {"role": "user", "content": 'hello'}],
   
#             temperature=0.8,
#             max_tokens=4096,
#             top_p=0.7,
#             stream=False
#             )
# response_text = completion.choices[0].message.content

# print(response_text)
