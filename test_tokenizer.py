from transformers import LlamaTokenizer

tokenizer_path = "/Users/laurensteel/.llama/checkpoints/Llama3.2-1B/tokenizer.model"

try:
    tokenizer = LlamaTokenizer.from_pretrained(tokenizer_path)
    print("Hugging Face tokenizer loaded successfully!")
except Exception as e:
    print(f"Error with Hugging Face tokenizer: {e}")

