"""
Main middleware - drop-in replacement for any LLM call.
Combines all optimization techniques.
"""

import os
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

class OptimizationLevel(Enum):
    MINIMAL = "minimal"      # Just output stripping
    STANDARD = "standard"    # + input cleaning + stop sequences
    AGGRESSIVE = "aggressive" # + language translation
    MAXIMUM = "maximum"      # + LLMLingua compression

@dataclass
class OptimizationStats:
    original_input_tokens: int = 0
    optimized_input_tokens: int = 0
    original_output_tokens: int = 0
    optimized_output_tokens: int = 0
    input_savings_percent: float = 0.0
    output_savings_percent: float = 0.0
    total_savings_percent: float = 0.0
    optimizations_applied: List[str] = field(default_factory=list)

class TokenOptimizerMiddleware:
    """
    Universal middleware for token optimization.
    
    Usage:
        optimizer = TokenOptimizerMiddleware(level=OptimizationLevel.AGGRESSIVE)
        
        # Wrap any LLM call
        response = optimizer.optimize(
            messages=[{"role": "user", "content": "Write a Python sort function"}],
            llm_call=your_llm_function
        )
    """
    
    def __init__(
        self,
        level: OptimizationLevel = OptimizationLevel.STANDARD,
        enable_translation: bool = False,
        enable_llmlingua: bool = False,
        target_language: str = "ZH",
        deepl_api_key: Optional[str] = None,
    ):
        self.level = level
        self.enable_translation = enable_translation or level in [OptimizationLevel.AGGRESSIVE, OptimizationLevel.MAXIMUM]
        self.enable_llmlingua = enable_llmlingua or level == OptimizationLevel.MAXIMUM
        self.target_language = target_language
        
        # Initialize components lazily
        self._translator = None
        self._compressor = None
        self._deepl_key = deepl_api_key
        
        # Stats tracking
        self.last_stats = None
        
        # Import tokenizer
        import tiktoken
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    @property
    def translator(self):
        if self._translator is None and self.enable_translation:
            from ..translators.deepl_translator import DeepLTokenOptimizer
            self._translator = DeepLTokenOptimizer(api_key=self._deepl_key)
        return self._translator
    
    @property
    def compressor(self):
        if self._compressor is None and self.enable_llmlingua:
            from ..optimizers.llmlingua_compressor import LLMLinguaOptimizer
            self._compressor = LLMLinguaOptimizer()
        return self._compressor
    
    def count_tokens(self, text: str) -> int:
        return len(self.tokenizer.encode(text))
    
    def optimize_input(self, messages: List[Dict]) -> List[Dict]:
        """Apply all input optimizations"""
        optimized = []
        optimizations = []
        
        for msg in messages:
            content = msg.get('content', '')
            original_tokens = self.count_tokens(content)
            
            # Step 1: Basic cleaning (always)
            content = self._clean_input(content)
            optimizations.append("basic_cleaning")
            
            # Step 2: Language translation (if enabled)
            if self.enable_translation and msg['role'] == 'user':
                result = self.translator.optimize(content)
                content = result.text
                if result.savings_percent > 5:
                    optimizations.append(f"translation_{self.target_language}")
            
            # Step 3: LLMLingua compression (if enabled)
            if self.enable_llmlingua:
                result = self.compressor.compress(content, target_ratio=0.6)
                content = result.compressed_prompt
                optimizations.append("llmlingua")
            
            optimized.append({
                'role': msg['role'],
                'content': content
            })
        
        return optimized, optimizations
    
    def _clean_input(self, text: str) -> str:
        """Basic input cleaning"""
        import re
        
        # Remove filler phrases
        fillers = [
            r'\bplease\b\s*',
            r'\bkindly\b\s*',
            r'\bcan you\b\s*',
            r'\bcould you\b\s*',
            r'\bwould you\b\s*',
            r'\bi would like you to\b\s*',
            r'\bi want you to\b\s*',
            r'\bi need you to\b\s*',
            r'\bif you don\'t mind\b\s*',
            r'\bthanks in advance\b\s*',
        ]
        
        result = text
        for filler in fillers:
            result = re.sub(filler, '', result, flags=re.IGNORECASE)
        
        # Compress whitespace
        result = ' '.join(result.split())
        
        return result
    
    def inject_output_constraints(self, messages: List[Dict], is_code_request: bool = True) -> List[Dict]:
        """Add constraints to minimize output"""
        
        if is_code_request:
            constraint = "\n\n[CRITICAL: Code only. No explanations. No markdown. No comments unless asked.]"
        else:
            constraint = "\n\n[Be extremely concise. No preamble. No pleasantries. Direct answer only.]"
        
        messages = [m.copy() for m in messages]
        
        # Add to system message or last user message
        for i, msg in enumerate(messages):
            if msg['role'] == 'system':
                messages[i]['content'] += constraint
                return messages
        
        if messages and messages[-1]['role'] == 'user':
            messages[-1]['content'] += constraint
        
        return messages
    
    def strip_output(self, text: str) -> str:
        """Remove unnecessary output content"""
        import re
        
        patterns = [
            r'^(sure|okay|certainly|of course|absolutely)[,!.\s]*',
            r'^(here\'?s?|here is|here are)[\w\s]*?:\s*',
            r'^(i\'?ll|let me|i will|i can)[\w\s]*?:\s*',
            r'```\w*\n?',
            r'```\s*$',
            r'\n\n(this|the) (code|function|script)[\s\S]*$',
            r'\n\nhope this helps[\s\S]*$',
            r'\n\nlet me know[\s\S]*$',
            r'\n\nfeel free[\s\S]*$',
        ]
        
        result = text
        for pattern in patterns:
            result = re.sub(pattern, '', result, flags=re.IGNORECASE | re.MULTILINE)
        
        return result.strip()
    
    def get_stop_sequences(self, is_code_request: bool = True) -> List[str]:
        """Get stop sequences based on request type"""
        from ..optimizers.provider_optimizations import StopSequenceOptimizer
        
        if is_code_request:
            return StopSequenceOptimizer.get_code_stop_sequences()
        return StopSequenceOptimizer.get_qa_stop_sequences()
    
    def optimize(
        self,
        messages: List[Dict],
        llm_call: Callable,
        is_code_request: bool = True,
        **llm_kwargs
    ) -> Dict[str, Any]:
        """
        Main optimization pipeline.
        
        Args:
            messages: Chat messages
            llm_call: Function that calls the LLM (takes messages, returns response string)
            is_code_request: Whether this is a code generation request
            **llm_kwargs: Additional kwargs passed to llm_call
        
        Returns:
            Dict with 'response' and 'stats'
        """
        
        # Track original tokens
        original_input = sum(self.count_tokens(m.get('content', '')) for m in messages)
        
        # Step 1: Optimize input
        optimized_messages, input_opts = self.optimize_input(messages)
        
        # Step 2: Add output constraints
        optimized_messages = self.inject_output_constraints(optimized_messages, is_code_request)
        
        # Step 3: Add stop sequences
        stop_sequences = self.get_stop_sequences(is_code_request)
        if 'stop' not in llm_kwargs:
            llm_kwargs['stop'] = stop_sequences
        
        # Track optimized input tokens
        optimized_input = sum(self.count_tokens(m.get('content', '')) for m in optimized_messages)
        
        # Step 4: Call LLM
        response = llm_call(messages=optimized_messages, **llm_kwargs)
        
        # Handle response format
        if isinstance(response, dict):
            response_text = response.get('content', response.get('text', str(response)))
        else:
            response_text = str(response)
        
        original_output = self.count_tokens(response_text)
        
        # Step 5: Strip output
        stripped_response = self.strip_output(response_text)
        
        # Step 6: Translate back if needed
        if self.enable_translation:
            stripped_response = self.translator.restore(stripped_response)
        
        optimized_output = self.count_tokens(stripped_response)
        
        # Calculate stats
        input_savings = ((original_input - optimized_input) / original_input * 100) if original_input > 0 else 0
        output_savings = ((original_output - optimized_output) / original_output * 100) if original_output > 0 else 0
        total_original = original_input + original_output
        total_optimized = optimized_input + optimized_output
        total_savings = ((total_original - total_optimized) / total_original * 100) if total_original > 0 else 0
        
        self.last_stats = OptimizationStats(
            original_input_tokens=original_input,
            optimized_input_tokens=optimized_input,
            original_output_tokens=original_output,
            optimized_output_tokens=optimized_output,
            input_savings_percent=round(input_savings, 2),
            output_savings_percent=round(output_savings, 2),
            total_savings_percent=round(total_savings, 2),
            optimizations_applied=input_opts + ["output_stripping", "stop_sequences"]
        )
        
        return {
            'response': stripped_response,
            'stats': self.last_stats
        }
        