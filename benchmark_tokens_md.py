
import time
import tiktoken
import os

# Read a large file to serve as sample text
with open("README.md", "r") as f:
    sample_text = f.read()

# Duplicate text to make it larger for measurable impact
text = sample_text * 1000
print(f"Sample text length: {len(text)} chars")

# Baseline: tiktoken
start_time = time.time()
encoding = tiktoken.get_encoding("cl100k_base")
tokens_tiktoken = len(encoding.encode(text, disallowed_special=()))
tiktoken_time = time.time() - start_time
print(f"tiktoken: {tokens_tiktoken} tokens in {tiktoken_time:.6f}s")

# Heuristic 1: len / 2.5
tokens_heuristic_25 = int(len(text) / 2.5)
print(f"Heuristic (2.5): {tokens_heuristic_25} tokens")
print(f"Error (2.5): {abs(tokens_tiktoken - tokens_heuristic_25) / tokens_tiktoken * 100:.2f}%")

# Heuristic 2: len / 3.0
tokens_heuristic_30 = int(len(text) / 3.0)
print(f"Heuristic (3.0): {tokens_heuristic_30} tokens")
print(f"Error (3.0): {abs(tokens_tiktoken - tokens_heuristic_30) / tokens_tiktoken * 100:.2f}%")

# Heuristic 3: len / 4.0 (standard approximation)
tokens_heuristic_40 = int(len(text) / 4.0)
print(f"Heuristic (4.0): {tokens_heuristic_40} tokens")
print(f"Error (4.0): {abs(tokens_tiktoken - tokens_heuristic_40) / tokens_tiktoken * 100:.2f}%")

# Calculate ideal factor
ideal_factor = len(text) / tokens_tiktoken
print(f"Ideal factor for this markdown file: {ideal_factor:.4f} chars/token")
