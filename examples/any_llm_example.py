"""Example: Works with ANY LLM"""

from src.middleware.token_optimizer import TokenOptimizerMiddleware, OptimizationLevel

optimizer = TokenOptimizerMiddleware(level=OptimizationLevel.STANDARD)

# Define your LLM call (works with anything)
def my_llm_call(messages, **kwargs):
    # Could be: OpenAI, Anthropic, Ollama, HuggingFace, vLLM, anything
    # Just return the response text
    import requests
    response = requests.post(
        "http://localhost:11434/api/chat",  # Ollama example
        json={"model": "llama2", "messages": messages, **kwargs}
    )
    return response.json()['message']['content']

# Use it
result = optimizer.optimize(
    messages=[{"role": "user", "content": "Write a quicksort function"}],
    llm_call=my_llm_call,
    is_code_request=True
)

print(result['response'])
