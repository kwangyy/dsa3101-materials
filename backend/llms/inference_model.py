import os
import json
from dotenv import load_dotenv
from llm_utils import create_llm_client, process_with_llm, process_files
import asyncio

load_dotenv()

inference_prompt = """Your task is to extract entities, as well as define any relationships between them, outputting only a single JSON object for which the format MUST be adhered to, with no other text. The entity types to extract are:

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

async def infer(input_json):
    if isinstance(input_json, dict):
        text_content = json.dumps(input_json, indent=2)
    else:
        text_content = str(input_json)

    formatted_input = {'text': text_content}
    client = create_llm_client("meta-llama/Llama-3.1-8B-Instruct", os.getenv("HF_TOKEN"))
    return await process_with_llm(client, formatted_input, inference_prompt, input_key="text")

def eval_text_files(input_folder, output_folder):
    client = create_llm_client("meta-llama/Llama-3.1-8B-Instruct", os.getenv("HF_TOKEN"))
    process_files(client, input_folder, output_folder, inference_prompt)

if __name__ == "__main__":
    async def test_inference():
        with open("../examples/example_response.txt", 'r') as file:
            json_obj = file.read()
            print(json_obj)

        answer = await infer(json_obj)
        with open("../examples/response_answer.json", "w") as file:
            json.dump(answer, file)
    
    asyncio.run(test_inference())
