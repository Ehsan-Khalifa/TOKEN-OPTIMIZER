"""Example: Using with OpenAI"""

from openai import OpenAI
from src.middleware.token_optimizer import TokenOptimizerMiddleware, OptimizationLevel

# Initialize
client = OpenAI()
optimizer = TokenOptimizerMiddleware(
    level=OptimizationLevel.AGGRESSIVE,
    enable_translation=True  # Use Chinese optimization
)

def call_openai(messages, **kwargs):
    """Wrapper for OpenAI API"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        **kwargs
    )
    return response.choices[0].message.content

# Use it
result = optimizer.optimize(
    messages=[
        {"role": "user", "content": "Please write me a Python function that takes a list of numbers and returns the sorted unique values, thanks!"}
    ],
    llm_call=call_openai,
    is_code_request=True,
    max_tokens=500
)

print(result['response'])
print(f"\nToken savings: {result['stats'].total_savings_percent}%")
