import json
import os
from dotenv import load_dotenv
from llm_utils import create_llm_client, process_with_llm
import asyncio

load_dotenv()

query_prompt = """You are a expert at ontology management, with a special focus in Enterprise Content Management. You can suggest an ontology as you deem fit. 

I am currently trying to create an ontology that is specific to a document. 

I have already set up an ontology beforehand, and the ontology rules are as such:
Person-Organization "AFFILIATED_WITH"
Person-Role Association "HAS_ROLE"
Person-Product/Service "INVOLVED_WITH"
Organization-Location "LOCATED_AT"

You do not need to use all of the rules in the ontology, only the ones that are relevant to the document.

With this, it is very important to follow these steps:
1. For each line in the ontology, check if there is such a relationship present in the text.
2. If there is a relationship, keep it with the relationship as is. Otherwise, exclude it from the ontology. Do NOT make up a relationship.
3. Return it in terms of JSON. 

An example has been given to you as such: 
{{
    "ontology": {{
        "entities": [
            {{
                "type": "Person",
                "properties": {{
                    "name": "string",
                    "affiliated_with": ["Organization"],
                    "roles": ["Role"],
                    "involved_with": ["Product/Service"]
                }}
            }},
            {{
                "type": "Organization",
                "properties": {{
                    "name": "string",
                    "located_at": "Location",
                    "collaborates_with": ["Organization"]
                }}
            }},
            {{
                "type": "Role",
                "properties": {{
                    "name": "string",
                    "assigned_to": ["Person"]
                }}
            }},
            {{
                "type": "Product/Service",
                "properties": {{
                    "name": "string",
                    "involves_person": ["Person"]
                }}
            }}
        ],
        "relationships": [
            {{
                "type": "AFFILIATED_WITH",
                "from": "Person",
                "to": "Organization"
            }},
            {{
                "type": "HAS_ROLE",
                "from": "Person",
                "to": "Role"
            }},
            {{
                "type": "INVOLVED_WITH",
                "from": "Person",
                "to": "Product/Service"
            }}
        ]
    }}
}}

The document is as such:
{document}
"""

async def infer(document):
    formatted_input = {'document': document}
    client = create_llm_client("meta-llama/Llama-3.1-8B-Instruct", os.getenv("HF_TOKEN"))
    return await process_with_llm(client, formatted_input, query_prompt, input_key="document")

if __name__ == "__main__":
    async def test_ontology():
        example_response_path = "../examples/example_response.txt"
        with open(example_response_path, "r") as file:
            document = file.read()
        answer = await infer(document)
        with open("../examples/ontology_answer.json", "w") as file:
            json.dump(answer, file)
    
    asyncio.run(test_ontology())
