from transformers import LlamaTokenizer

tokenizer_path = "/Users/laurensteel/Documents/5X/cap_stone/my_git/models/Llama3.2-1B"
tokenizer = LlamaTokenizer.from_pretrained(tokenizer_path, legacy=True)
print("Tokenizer loaded successfully!")


