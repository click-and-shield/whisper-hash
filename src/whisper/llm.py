import tiktoken
import json

def calculate_tokens(prompt: str, model: str = "gpt-4") -> int:
    """Calculate the number of tokens used by a prompt."""
    encoding = tiktoken.encoding_for_model(model)
    p: list[dict[str, str]] = json.loads(prompt)
    total = 0
    for m in p:
        total += 4
        total += len(encoding.encode(m["content"]))
        total += len(encoding.encode(m["role"]))
    total += 2
    return total

