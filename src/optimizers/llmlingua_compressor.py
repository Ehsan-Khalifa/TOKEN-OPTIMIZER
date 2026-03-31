"""
LLMLingua integration - Microsoft's proven prompt compression.
Paper: https://arxiv.org/abs/2310.05736
GitHub: https://github.com/microsoft/LLMLingua

Achieves 2x-20x compression with minimal quality loss.
"""

from llmlingua import PromptCompressor as LLMLinguaCompressor
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class CompressionResult:
    compressed_prompt: str
    original_tokens: int
    compressed_tokens: int
    compression_ratio: float
    saving_percent: float

class LLMLinguaOptimizer:
    """
    Production-ready LLMLingua wrapper.
    
    HOW IT WORKS:
    1. Uses small LLM to calculate perplexity of each token
    2. Removes low-information tokens (predictable ones)
    3. Keeps high-information tokens (surprising/important ones)
    4. Maintains semantic meaning while reducing tokens
    
    PROVEN RESULTS (from Microsoft paper):
    - GSM8K: 20x compression, 95% accuracy retention
    - BBH: 10x compression, 92% accuracy retention
    """
    
    def __init__(
        self,
        model_name: str = "microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank",
        device: str = "cpu",  # Use "cuda" if GPU available
        use_llmlingua2: bool = True  # v2 is faster and better
    ):
        """
        Initialize compressor.
        
        Models available:
        - "microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank" (recommended, fast)
        - "NousResearch/Llama-2-7b-hf" (better quality, slower)
        - "gpt2" (fastest, lower quality)
        """
        
        self.compressor = LLMLinguaCompressor(
            model_name=model_name,
            device_map=device,
            use_llmlingua2=use_llmlingua2
        )
    
    def compress(
        self,
        prompt: str,
        target_ratio: float = 0.5,  # Keep 50% of tokens
        context: Optional[str] = None,
        instruction: Optional[str] = None,
        force_tokens: Optional[list] = None,  # Tokens to never remove
        force_reserve_digit: bool = True,  # Keep numbers
        drop_consecutive: bool = True,  # Remove repeated patterns
    ) -> CompressionResult:
        """
        Compress a prompt while preserving meaning.
        
        Args:
            prompt: The prompt to compress
            target_ratio: Target compression ratio (0.5 = keep 50%)
            context: Optional context that helps compression
            instruction: Optional instruction part (compressed less aggressively)
            force_tokens: List of tokens to never remove
            force_reserve_digit: Keep all numbers
            drop_consecutive: Remove consecutive repeated tokens
        
        Returns:
            CompressionResult with compressed prompt and stats
        """
        
        # Build compression request
        if context and instruction:
            # Structured compression (best results)
            result = self.compressor.compress_prompt(
                context=context,
                instruction=instruction,
                question=prompt,
                rate=target_ratio,
                force_tokens=force_tokens or ['?', '!', '.', '\n', 'code', 'function', 'return'],
                force_reserve_digit=force_reserve_digit,
                drop_consecutive=drop_consecutive
            )
        else:
            # Simple compression
            result = self.compressor.compress_prompt(
                prompt,
                rate=target_ratio,
                force_tokens=force_tokens or ['?', '!', '.', '\n'],
                force_reserve_digit=force_reserve_digit,
                drop_consecutive=drop_consecutive
            )
        
        original_tokens = result.get('origin_tokens', len(prompt.split()))
        compressed_tokens = result.get('compressed_tokens', len(result['compressed_prompt'].split()))
        
        return CompressionResult(
            compressed_prompt=result['compressed_prompt'],
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=result.get('rate', target_ratio),
            saving_percent=round((1 - compressed_tokens/original_tokens) * 100, 2) if original_tokens > 0 else 0
        )
    
    def compress_for_code(
        self,
        prompt: str,
        code_context: Optional[str] = None,
        target_ratio: float = 0.6  # Less aggressive for code
    ) -> CompressionResult:
        """
        Specialized compression for coding prompts.
        Preserves code-related tokens more carefully.
        """
        
        code_tokens = [
            'function', 'def', 'class', 'return', 'if', 'else', 'for', 'while',
            'import', 'from', 'const', 'let', 'var', 'async', 'await',
            '{', '}', '(', ')', '[', ']', ':', ';', '=', '=>', '->',
            'true', 'false', 'null', 'None', 'undefined',
            'try', 'catch', 'except', 'finally', 'throw', 'raise',
        ]
        
        return self.compress(
            prompt=prompt,
            context=code_context,
            target_ratio=target_ratio,
            force_tokens=code_tokens,
            force_reserve_digit=True
        )