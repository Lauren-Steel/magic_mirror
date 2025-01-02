from transformers import AutoTokenizer, AutoModelForCausalLM

# Path to the downloaded model
MODEL_PATH = "/Users/laurensteel/.llama/checkpoints/Llama3.2-1B"

# Load the tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH)

# Create a prompt
prompt = "What is the capital of Canada?"

# Tokenize the prompt
inputs = tokenizer(prompt, return_tensors="pt")

# Generate a response
outputs = model.generate(inputs["input_ids"], max_length=50)

# Decode and print the response
response = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(response)
