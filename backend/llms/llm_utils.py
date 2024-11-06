import re
import json
import os
from typing import Optional, Dict, Any, Callable
from huggingface_hub import InferenceClient

def extract_json_from_response(response_text: str) -> Optional[Dict[str, Any]]:
    """
    Extracts JSON from response text, handling code blocks and multiline content.
    Removes comments before parsing.
    """
    def remove_comments(json_str):
        json_str = re.sub(r'#.*$', '', json_str, flags=re.MULTILINE)
        json_str = re.sub(r'//.*$', '', json_str, flags=re.MULTILINE)
        json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
        return json_str

    # First try to find JSON within code blocks
    code_block_pattern = r'```json\s*([\s\S]*?)\s*```'
    code_block_match = re.search(code_block_pattern, response_text)
    
    if code_block_match:
        try:
            json_str = code_block_match.group(1)
            json_str = remove_comments(json_str)
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass

    # If no code block or invalid JSON, try general JSON pattern
    json_pattern = r'(?s)\{.*?\}(?=\s*$)'
    json_match = re.search(json_pattern, response_text)
    
    if json_match:
        try:
            json_str = json_match.group(0)
            json_str = remove_comments(json_str)
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass

    return None

def create_llm_client(model_name: str, api_key: str) -> InferenceClient:
    """Creates a new LLM client with the specified model and API key."""
    return InferenceClient(model_name, api_key=api_key)

def process_with_llm(
    client: InferenceClient,
    input_data: Dict[str, Any],
    prompt_template: str,
    input_key: str = "data",
    temperature: float = 0.8,
    max_tokens: int = 4096,
    top_p: float = 0.7
) -> Optional[Dict[str, Any]]:
    """
    Process input data using the specified prompt template and model.
    """
    if not isinstance(input_data, dict) or input_key not in input_data:
        raise ValueError(f"Input must be a dictionary with a '{input_key}' key")
    
    content = input_data[input_key]
    populated_prompt = prompt_template.format(**{input_key: content})
    
    print("Processing input...")
    completion = client.chat.completions.create(
        model=client.model,
        messages=[
            {"role": "user", "content": populated_prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        stream=False
    )
    response_text = completion.choices[0].message.content
    print(response_text)
    
    extracted_json = extract_json_from_response(response_text)
    print("Processing complete")
    return extracted_json

def process_files(
    client: InferenceClient,
    input_folder: str,
    output_folder: str,
    prompt_template: str,
    input_key: str = "text"
) -> None:
    """
    Process multiple text files using the specified prompt template and model.
    """
    if not os.path.exists(input_folder):
        print(f"The folder '{input_folder}' does not exist.")
        return

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    txt_files = [f for f in os.listdir(input_folder) if f.endswith('.txt')]

    for txt_file in txt_files:
        txt_file_path = os.path.join(input_folder, txt_file)
        base_name = os.path.splitext(txt_file)[0]
        evaluated_filename = f"{base_name}_evaluated.json"
        evaluated_file_path = os.path.join(output_folder, evaluated_filename)

        if os.path.exists(evaluated_file_path):
            print(f"Skipping '{txt_file}' as '{evaluated_filename}' already exists.")
            continue

        with open(txt_file_path, 'r') as file:
            text_content = file.read()

        input_data = {input_key: text_content}
        extracted_json = process_with_llm(client, input_data, prompt_template, input_key)

        if extracted_json:
            with open(evaluated_file_path, 'w') as output_file:
                json.dump(extracted_json, output_file, indent=4)
            print(f"Processed '{txt_file}' and saved to '{evaluated_filename}'.")
        else:
            print(f"Failed to process '{txt_file}'.") 