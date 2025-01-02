from transformers import LlamaTokenizer

tokenizer_path = "/Users/laurensteel/Documents/5X/cap_stone/my_git/models/Llama3.2-1B/tokenizer.model"

try:
    tokenizer = LlamaTokenizer(vocab_file=tokenizer_path, legacy=True)
    print("Tokenizer loaded successfully!")
except Exception as e:
    print(f"Error loading tokenizer: {e}")

