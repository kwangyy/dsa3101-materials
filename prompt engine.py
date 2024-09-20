from transformers import BartTokenizer, BartForConditionalGeneration

# Load the fine-tuned model and tokenizer
model = BartForConditionalGeneration.from_pretrained('/Users/falariee/Desktop/fine_tuned_bart')
tokenizer = BartTokenizer.from_pretrained('/Users/falariee/Desktop/fine_tuned_bart')

# Function to generate response based on a test prompt
def test_model(prompt):
    # Tokenize the input prompt
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, padding="max_length", max_length=64)
    
    # Generate output using the model
    output_ids = model.generate(inputs['input_ids'], max_length=64, num_beams=4, early_stopping=True)
    
    # Decode the output tokens to text
    response = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return response

# Test the model with a sample query
test_query = "What is the relation between Bob Johnson and AI 101?"
response = test_model(test_query)

print("Prompt:", test_query)
print("Response:", response)
