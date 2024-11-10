import re
import json
import os
from typing import Optional, Dict, Any, Callable, AsyncGenerator
from huggingface_hub import AsyncInferenceClient

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

def create_llm_client(model_name: str, api_key: str) -> AsyncInferenceClient:
    """Creates a new LLM client with the specified model and API key."""
    return AsyncInferenceClient(
        model=model_name,
        token=api_key
    )

async def process_with_llm(
    client: AsyncInferenceClient,
    input_data: Dict[str, Any],
    prompt_template: str,
    input_key: str = "data",
    temperature: float = 0.8,
    max_tokens: int = 4096,
    top_p: float = 0.7,
    json_output: bool = True
) -> Dict[str, Any]:
    try:
        # Handle both string and list input keys
        if isinstance(input_key, str):
            populated_prompt = prompt_template.format(**{input_key: input_data[input_key]})
        else:
            populated_prompt = prompt_template.format(**{k: input_data[k] for k in input_key})

        print(f"Sending prompt to LLM: {populated_prompt}")
        
        # Create the completion
        completion = await client.chat.completions.create(
            model=client.model,
            messages=[
                {"role": "user", "content": populated_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p
        )
        
        # Get the response text from the completion
        response_text = completion.choices[0].message.content
        print(f"Raw LLM response: {response_text}")
        
        if json_output:
            try:
                # Try to parse as JSON first
                return json.loads(response_text)
            except json.JSONDecodeError:
                # If not valid JSON, extract JSON from the text
                extracted_json = extract_json_from_response(response_text)
                if extracted_json is not None:
                    return extracted_json
                # If no JSON found, return as content
                return {"content": response_text}
        
        return {"content": response_text}
        
    except Exception as e:
        print(f"Error in process_with_llm: {str(e)}")
        if json_output:
            return {"error": str(e)}
        return {"content": f"Error: {str(e)}"}

def process_files(
    client: AsyncInferenceClient,
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

async def process_with_llm_stream(
    client: AsyncInferenceClient,
    input_data: Dict[str, Any],
    prompt_template: str,
    input_key: str = "data",
    temperature: float = 0.8,
    max_tokens: int = 4096,
    top_p: float = 0.7,
) -> AsyncGenerator[str, None]:
    try:
        if isinstance(input_key, str):
            populated_prompt = prompt_template.format(**{input_key: input_data[input_key]})
        else:
            populated_prompt = prompt_template.format(**{k: input_data[k] for k in input_key})

        stream = await client.chat.completions.create(
            model=client.model,
            messages=[{"role": "user", "content": populated_prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            stream=True
        )

        response_text = ""
        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                response_text += chunk.choices[0].delta.content
                try:
                    # Try to parse accumulated text as JSON
                    json_response = json.loads(response_text)
                    yield json_response.get("response", "")
                    break
                except json.JSONDecodeError:
                    # If not valid JSON yet, continue accumulating
                    continue

    except Exception as e:
        yield f"Error: {str(e)}"