"""Example: Using with Anthropic (with caching)"""

import anthropic
from src.middleware.token_optimizer import TokenOptimizerMiddleware, OptimizationLevel
from src.optimizers.provider_optimizations import AnthropicOptimizer

# Initialize
optimizer = TokenOptimizerMiddleware(level=OptimizationLevel.AGGRESSIVE)
anthropic_opt = AnthropicOptimizer()

# Use with caching and prefill
result = anthropic_opt.chat_with_caching(
    messages=[
        {"role": "user", "content": "Write a binary search function in Python"}
    ],
    system="You are a coding assistant. Output code only, no explanations.",
    prefill="def binary_search(",  # Force the response to start this way
    max_tokens=500
)

print(result['content'])
print(f"Cache stats: {result['cache_stats']}")
