"""
Benchmark tests for token savings measurement.
"""

import pytest
import json
import time
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict

pytestmark = pytest.mark.benchmark

@dataclass
class BenchmarkResult:
    """Result of a single benchmark run"""
    test_name: str
    original_tokens: int
    optimized_tokens: int
    savings_percent: float
    optimization_level: str
    latency_ms: float

class TestTokenSavingsBenchmarks:
    """Benchmarks for measuring actual token savings"""
    
    @pytest.fixture
    def benchmark_prompts(self) -> List[Dict]:
        """Realistic prompts for benchmarking"""
        return [
            {
                "name": "simple_code_request",
                "prompt": "Can you please write me a Python function that takes a list of numbers and returns only the even ones?",
                "type": "code"
            },
            {
                "name": "verbose_code_request",
                "prompt": "I was wondering if you could possibly help me out with something. I need a JavaScript function that will take an array of objects.",
                "type": "code"
            },
            {
                "name": "debug_request",
                "prompt": "Hey, I'm having some trouble with my code. Could you please take a look at this and help me figure out what's wrong?",
                "type": "debug"
            },
            {
                "name": "explanation_request",
                "prompt": "Could you please explain to me how decorators work in Python?",
                "type": "explain"
            },
            {
                "name": "minimal_prompt",
                "prompt": "Sort function Python",
                "type": "code"
            },
        ]
    
    @pytest.fixture
    def results_file(self, tmp_path) -> Path:
        """Path for storing benchmark results"""
        return tmp_path / "benchmark_results.json"
    
    def test_benchmark_token_counting(self, benchmark_prompts, token_counter):
        """Benchmark token counting"""
        results = []
        
        for prompt_data in benchmark_prompts:
            tokens = token_counter(prompt_data["prompt"])
            results.append({
                "prompt": prompt_data["name"],
                "tokens": tokens
            })
        
        # Print results
        print("\n=== Token Count Benchmarks ===")
        for result in results:
            print(f"{result['prompt']}: {result['tokens']} tokens")
        
        # All should have at least 1 token
        assert all(r['tokens'] > 0 for r in results)
    
    def test_average_tokens_per_word(self, benchmark_prompts, token_counter):
        """Calculate average tokens per word"""
        ratios = []
        
        for prompt_data in benchmark_prompts:
            tokens = token_counter(prompt_data["prompt"])
            words = len(prompt_data["prompt"].split())
            ratio = tokens / words if words > 0 else 0
            ratios.append(ratio)
        
        avg_ratio = sum(ratios) / len(ratios) if ratios else 0
        print(f"\n=== Average Tokens per Word ===")
        print(f"Average ratio: {avg_ratio:.2f}")
        
        # Should be between 0.5 and 2 tokens per word typically
        assert 0.5 < avg_ratio < 2.0
    
    def test_output_samples_token_count(self, sample_llm_responses, token_counter):
        """Benchmark token count for LLM responses"""
        print("\n=== LLM Response Token Counts ===")
        
        for i, response_data in enumerate(sample_llm_responses, 1):
            original_tokens = token_counter(response_data["input"])
            print(f"Response {i}: {original_tokens} tokens")
            assert original_tokens > 0
    
    def test_latency_of_token_counting(self, token_counter):
        """Measure latency of token counting"""
        test_text = "Write a Python function to sort an array. Please make it efficient and include comments."
        
        times = []
        for _ in range(10):
            start = time.perf_counter()
            token_counter(test_text)
            elapsed = (time.perf_counter() - start) * 1000  # in ms
            times.append(elapsed)
        
        avg_time = sum(times) / len(times)
        print(f"\n=== Token Counter Latency ===")
        print(f"Average latency: {avg_time:.3f}ms (10 runs)")
        
        # Should be fast (< 10ms)
        assert avg_time < 10
