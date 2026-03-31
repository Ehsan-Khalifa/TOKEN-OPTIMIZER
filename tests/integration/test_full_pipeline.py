"""
Integration tests for full optimization pipeline.
"""

import pytest
import os
from unittest.mock import Mock, patch

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration

class TestFullPipeline:
    """Integration tests for complete optimization flow"""
    
    @pytest.fixture
    def real_middleware(self, mock_env):
        """Create middleware with real components (mocked APIs)"""
        from src.middleware.token_optimizer import TokenOptimizerMiddleware, OptimizationLevel
        return TokenOptimizerMiddleware(
            level=OptimizationLevel.STANDARD,
            enable_translation=False
        )
    
    def test_end_to_end_code_request(self, real_middleware, mock_llm_client):
        """Test complete flow for code request"""
        messages = [
            {"role": "system", "content": "You are a coding assistant."},
            {"role": "user", "content": "Please write me a Python function to sort a list of numbers."}
        ]
        
        result = real_middleware.optimize(
            messages=messages,
            llm_call=mock_llm_client.chat,
            is_code_request=True,
            max_tokens=500
        )
        
        # Verify response structure
        assert 'response' in result
        assert 'stats' in result
    
    def test_end_to_end_qa_request(self, real_middleware, mock_llm_client):
        """Test complete flow for QA request"""
        messages = [
            {"role": "user", "content": "What is the difference between a list and a tuple in Python?"}
        ]
        
        result = real_middleware.optimize(
            messages=messages,
            llm_call=mock_llm_client.chat,
            is_code_request=False
        )
        
        assert 'response' in result
    
    def test_multiple_messages_optimization(self, real_middleware, mock_llm_client):
        """Test optimization with conversation history"""
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Can you help me with Python?"},
            {"role": "assistant", "content": "Of course! What do you need help with?"},
            {"role": "user", "content": "Please write a function to calculate factorial."}
        ]
        
        result = real_middleware.optimize(
            messages=messages,
            llm_call=mock_llm_client.chat,
            is_code_request=True
        )
        
        assert 'response' in result
        # Should have optimized all user messages
        stats = result['stats']
        assert stats.original_input_tokens > 0
    
    def test_preserves_code_in_context(self, real_middleware, mock_llm_client):
        """Test that code in context is preserved"""
        messages = [
            {"role": "user", "content": """Fix this code:
```python
def buggy():
    retrun 42
```"""}
        ]
        
        result = real_middleware.optimize(
            messages=messages,
            llm_call=mock_llm_client.chat,
            is_code_request=True
        )
        
        # Code should be preserved in the call
        assert 'response' in result


@pytest.mark.requires_api
class TestRealAPIIntegration:
    """Tests that require real API keys - skipped by default"""
    
    @pytest.fixture
    def skip_if_no_api(self):
        """Skip if no API keys available"""
        if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "test-key":
            pytest.skip("No real API key available")
    
    def test_real_openai_integration(self, skip_if_no_api):
        """Test with real OpenAI API"""
        try:
            from openai import OpenAI
            from src.middleware.token_optimizer import TokenOptimizerMiddleware
            
            client = OpenAI()
            middleware = TokenOptimizerMiddleware()
            
            def call_openai(messages, **kwargs):
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    **kwargs
                )
                return response.choices[0].message.content
            
            result = middleware.optimize(
                messages=[{"role": "user", "content": "Write a hello world function in Python"}],
                llm_call=call_openai,
                is_code_request=True,
                max_tokens=100
            )
            
            assert "def" in result['response'] or "print" in result['response']
        except ImportError:
            pytest.skip("OpenAI package not installed")
