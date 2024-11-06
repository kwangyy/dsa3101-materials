from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("HF_TOKEN")
client = InferenceClient("meta-llama/Llama-3.1-8B-Instruct", api_key=api_key)

completion = client.chat.completions.create(
            messages=[ 
                {"role": "user", "content": "hello"}],
   
            temperature=0.8,
            max_tokens=4096,
            top_p=0.7,
            stream=False
            )
response_text = completion.choices[0].message.content
print(response_text)