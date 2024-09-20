import pandas as pd
from transformers import BartTokenizer, BartForConditionalGeneration, Trainer, TrainingArguments
from datasets import Dataset

# Load the augmented dataset from your file path
data = pd.read_csv('/Users/falariee/Desktop/Augmented_Graph_Dataset.csv')

# Convert the data into prompt-response pairs for the model
def create_prompt_response(row):
    prompt = f"What is the relation between {row['head_node']} and {row['tail_node']}?"
    response = f"{row['head_node']} {row['relationship']} {row['tail_node']}."
    return {'prompt': prompt, 'response': response}

# Apply the function to create the training dataset
train_data = data.apply(create_prompt_response, axis=1)
train_dataset = Dataset.from_pandas(pd.DataFrame(train_data.tolist()))

# Tokenizer and model
tokenizer = BartTokenizer.from_pretrained('facebook/bart-base')
model = BartForConditionalGeneration.from_pretrained('facebook/bart-base')

# Tokenize the dataset
# Tokenize the dataset with padding and truncation for both inputs and labels
def tokenize_function(examples):
    model_inputs = tokenizer(examples['prompt'], padding="max_length", truncation=True, max_length=64)
    labels = tokenizer(examples['response'], padding="max_length", truncation=True, max_length=64)
    
    model_inputs['labels'] = labels['input_ids']
    return model_inputs

tokenized_dataset = train_dataset.map(tokenize_function, batched=True)


# Training arguments
training_args = TrainingArguments(
    output_dir="/Users/falariee/Desktop/results",
    evaluation_strategy="epoch",  # Keep this as "epoch"
    save_strategy="epoch",        # Ensure saving happens after each epoch
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=70,
    weight_decay=0.01,
    logging_dir="/Users/falariee/Desktop/logs",
    save_total_limit=3,
    logging_steps=100,
    eval_steps=100,
    load_best_model_at_end=True,  # Now both strategies match
    metric_for_best_model="loss"
)


# Trainer setup
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    eval_dataset=tokenized_dataset,  # You can split the dataset for proper evaluation
    tokenizer=tokenizer
)

# Train the model
trainer.train()

# Save the fine-tuned model
model.save_pretrained('/Users/falariee/Desktop/fine_tuned_bart')
tokenizer.save_pretrained('/Users/falariee/Desktop/fine_tuned_bart')
