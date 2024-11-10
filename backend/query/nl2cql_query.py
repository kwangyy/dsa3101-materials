from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

# Load the model and tokenizer
model = AutoModelForSeq2SeqLM.from_pretrained("Chirayu/nl2cql")
tokenizer = AutoTokenizer.from_pretrained("Chirayu/nl2cql")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

def generate_query(
        textual_query: str,
        num_beams: int = 10,
        max_length: int = 128,
        repetition_penalty: int = 2.5,
        length_penalty: int = 1,
        early_stopping: bool = True,
        top_p: float = 0.95,
        top_k: int = 50,
        num_return_sequences: int = 1,
    ) -> str:
        input_ids = tokenizer.encode(
            textual_query, return_tensors="pt", add_special_tokens=True
        ).to(device)
        
        generated_ids = model.generate(
            input_ids=input_ids,
            num_beams=num_beams,
            max_length=max_length,
            repetition_penalty=repetition_penalty,
            length_penalty=length_penalty,
            early_stopping=early_stopping,
            top_p=top_p,
            top_k=top_k,
            num_return_sequences=num_return_sequences,
        )
        
        query = tokenizer.decode(
            generated_ids[0], skip_special_tokens=True, clean_up_tokenization_spaces=True
        )
        return query

def generate_cypher(data):
    natural_language_prompt = data.get("prompt")
    
    if not natural_language_prompt:
        return {"error": "No prompt provided"}
    
    # Generate the Cypher query
    cypher_query = generate_query(natural_language_prompt)
    
    # Optional: Validate the query against dataset columns
    # Implement any validation if required based on your dataset
    # Example: Check if entities in cypher_query are present in the graph_data columns

    return {"cypher_query": cypher_query}
if __name__ == '__main__':
    data = {"prompt": "What are the names of the people who work at IBM?"}
    print(generate_cypher(data))
