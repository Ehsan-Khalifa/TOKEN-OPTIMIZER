"""
Provider-specific optimizations that ACTUALLY save tokens.
These are official features, not hacks.
"""

import os
import hashlib
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

# ============================================
# ANTHROPIC: Prompt Caching + Response Prefill
# ============================================

class AnthropicOptimizer:
    """
    Anthropic-specific optimizations.
    
    1. PROMPT CACHING (official feature):
       - Cache large system prompts/context
       - 90% cost reduction on cache hits
       - Minimum 1024 tokens to cache
       
    2. RESPONSE PREFILLING:
       - Start the response yourself
       - Forces specific format
       - Reduces verbose preamble
    """
    
    def __init__(self, api_key: Optional[str] = None):
        import anthropic
        self.client = anthropic.Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        self.cache_enabled = True
    
    def chat_with_caching(
        self,
        messages: List[Dict],
        system: str,
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 1024,
        prefill: Optional[str] = None,  # Start the response
    ) -> Dict[str, Any]:
        """
        Chat with prompt caching and optional prefilling.
        
        PROMPT CACHING:
        - Add cache_control to messages/system
        - Cached content is 90% cheaper on reuse
        - Great for: system prompts, documentation, examples
        
        PREFILLING:
        - Add assistant message with start of response
        - Model continues from there
        - Eliminates "Sure, here's..." preamble
        """
        
        # Build system with cache control
        system_with_cache = [
            {
                "type": "text",
                "text": system,
                "cache_control": {"type": "ephemeral"}  # Cache for 5 minutes
            }
        ]
        
        # Add prefill if specified
        if prefill:
            messages = messages.copy()
            messages.append({
                "role": "assistant",
                "content": prefill
            })
        
        response = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_with_cache,
            messages=messages
        )
        
        # Get cache stats
        usage = response.usage
        cache_stats = {
            "input_tokens": usage.input_tokens,
            "output_tokens": usage.output_tokens,
            "cache_creation_input_tokens": getattr(usage, 'cache_creation_input_tokens', 0),
            "cache_read_input_tokens": getattr(usage, 'cache_read_input_tokens', 0),
        }
        
        return {
            "content": response.content[0].text,
            "cache_stats": cache_stats,
            "savings_from_cache": cache_stats["cache_read_input_tokens"] * 0.9  # 90% saved
        }
    
    def code_response_prefills(self) -> Dict[str, str]:
        """
        Prefills that force code-only output.
        Use these to eliminate verbose preambles.
        """
        return {
            "python": "```python\n",
            "javascript": "```javascript\n",
            "typescript": "```typescript\n",
            "rust": "```rust\n",
            "go": "```go\n",
            "generic": "```\n",
            "json": "{\n",
            "direct": "",  # No preamble at all
        }


# ============================================
# OPENAI: Structured Outputs + Caching
# ============================================

class OpenAIOptimizer:
    """
    OpenAI-specific optimizations.
    
    1. STRUCTURED OUTPUTS (JSON mode):
       - Forces JSON response
       - No prose explanations
       - More predictable token usage
       
    2. PREDICTED OUTPUTS:
       - Tell API what output will look like
       - Speeds up generation
       - Reduces variability
       
    3. PROMPT CACHING (automatic):
       - Automatic for prompts > 1024 tokens
       - 50% discount on cached tokens
    """
    
    def __init__(self, api_key: Optional[str] = None):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
    
    def chat_json_mode(
        self,
        messages: List[Dict],
        model: str = "gpt-4o",
        max_tokens: int = 1024
    ) -> Dict[str, Any]:
        """
        Force JSON output - eliminates prose entirely.
        """
        
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            response_format={"type": "json_object"}
        )
        
        return {
            "content": response.choices[0].message.content,
            "usage": {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
                "cached_tokens": getattr(response.usage, 'prompt_tokens_details', {}).get('cached_tokens', 0)
            }
        }
    
    def chat_with_prediction(
        self,
        messages: List[Dict],
        predicted_output: str,  # What you expect the output to be
        model: str = "gpt-4o",
        max_tokens: int = 1024
    ) -> Dict[str, Any]:
        """
        Use predicted outputs for faster, cheaper responses.
        Great for code refactoring where output is similar to input.
        """
        
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            prediction={
                "type": "content",
                "content": predicted_output
            }
        )
        
        return {
            "content": response.choices[0].message.content,
            "usage": response.usage
        }


# ============================================
# STOP SEQUENCES - Works on all providers
# ============================================

class StopSequenceOptimizer:
    """
    Stop sequences cut off generation early.
    Prevents verbose explanations after code.
    """
    
    @staticmethod
    def get_code_stop_sequences() -> List[str]:
        """Stop sequences that cut off post-code explanations"""
        return [
            "\n\nThis code",
            "\n\nThis function",
            "\n\nThis will",
            "\n\nHere's how",
            "\n\nExplanation:",
            "\n\nHow it works:",
            "\n\nNote:",
            "\n\nNotes:",
            "\n\n---",
            "\nLet me",
            "\nI hope",
            "\nFeel free",
        ]
    
    @staticmethod
    def get_qa_stop_sequences() -> List[str]:
        """Stop after first complete answer"""
        return [
            "\n\nHowever",
            "\n\nThat said",
            "\n\nIt's worth noting",
            "\n\nAdditionally",
            "\n\nFurthermore",
            "\n\nIn addition",
        ]
        