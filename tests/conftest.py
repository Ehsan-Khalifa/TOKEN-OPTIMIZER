"""
Pytest configuration and shared fixtures.
"""

import os
import sys
import pytest
from unittest.mock import Mock, MagicMock
from typing import List, Dict, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# ============================================
# ENVIRONMENT FIXTURES
# ============================================

@pytest.fixture(scope="session")
def env_setup():
    """Setup environment variables for testing"""
    os.environ.setdefault("DEEPL_API_KEY", "test-key")
    os.environ.setdefault("OPENAI_API_KEY", "test-key")
    os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")
    yield
    # Cleanup if needed

@pytest.fixture
def mock_env(monkeypatch):
    """Mock environment variables"""
    monkeypatch.setenv("DEEPL_API_KEY", "mock-deepl-key")
    monkeypatch.setenv("OPENAI_API_KEY", "mock-openai-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "mock-anthropic-key")

# ============================================
# SAMPLE DATA FIXTURES
# ============================================

@pytest.fixture
def sample_prompts() -> List[Dict[str, str]]:
    """Sample prompts for testing"""
    return [
        {
            "input": "Can you please write me a Python function that sorts a list?",
            "expected_cleaned": "write python function sorts list",
            "type": "code"
        },
        {
            "input": "I would like you to help me debug this code please",
            "expected_cleaned": "debug this code",
            "type": "debug"
        },
        {
            "input": "What is a decorator in Python?",
            "expected_cleaned": "what is decorator in python",
            "type": "question"
        },
        {
            "input": "Could you kindly explain how async/await works?",
            "expected_cleaned": "explain how async/await works",
            "type": "explain"
        }
    ]

@pytest.fixture
def sample_code_prompts() -> List[str]:
    """Sample code-specific prompts"""
    return [
        "Write a function to reverse a string",
        "Create a class for a binary search tree",
        "Implement quicksort in Python",
        "Write a REST API endpoint using FastAPI",
        "Create a React component for a todo list",
    ]

@pytest.fixture
def sample_llm_responses() -> List[Dict[str, str]]:
    """Sample LLM responses with bloat"""
    return [
        {
            "input": """Sure, here's a Python function that reverses a string:

```python
def reverse_string(s):
    return s[::-1]
```

This function works by using Python's slice notation with a step of -1, which reverses the string. Let me know if you need any clarification!""",
            "expected_stripped": """def reverse_string(s):
    return s[::-1]"""
        },
        {
            "input": """Certainly! I'd be happy to help you with that. Here is the code:

```javascript
function add(a, b) {
    return a + b;
}
```

Hope this helps! Feel free to ask if you have any questions.""",
            "expected_stripped": """function add(a, b) {
    return a + b;
}"""
        },
        {
            "input": """Of course! Here's a simple implementation:

```python
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
```

This is a recursive implementation of factorial. The base case is when n is 0 or 1, and it returns 1. Otherwise, it multiplies n by the factorial of n-1.""",
            "expected_stripped": """def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)"""
        }
    ]

@pytest.fixture
def sample_messages() -> List[Dict[str, Any]]:
    """Sample chat messages"""
    return [
        {"role": "system", "content": "You are a helpful coding assistant."},
        {"role": "user", "content": "Please write a function to calculate fibonacci numbers."}
    ]

# ============================================
# MOCK FIXTURES
# ============================================

@pytest.fixture
def mock_llm_client():
    """Mock LLM client that returns predictable responses"""
    client = Mock()

    def mock_chat(messages, **kwargs):
        # Return response based on input
        user_msg = next((m['content'] for m in messages if m['role'] == 'user'), '')
        
        if 'fibonacci' in user_msg.lower():
            return """Here's a fibonacci function:

```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

This uses recursion to calculate fibonacci numbers."""

        if 'sort' in user_msg.lower():
            return """```python
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)
```"""
        
        return "Response to: " + user_msg

    client.chat = Mock(side_effect=mock_chat)
    return client

@pytest.fixture
def mock_deepl_translator():
    """Mock DeepL translator"""
    translator = Mock()

    def mock_translate(text, target_lang="ZH", **kwargs):
        result = Mock()
        # Simulate translation (just return mock Chinese)
        if target_lang == "ZH":
            result.text = f"[ZH]{text}[/ZH]"  # Mock translation
        else:
            result.text = text.replace("[ZH]", "").replace("[/ZH]", "")
        return result

    translator.translate_text = Mock(side_effect=mock_translate)
    return translator

@pytest.fixture
def mock_tiktoken():
    """Mock tiktoken encoder"""
    encoder = Mock()
    encoder.encode = Mock(side_effect=lambda x: list(x.split()))  # Simple word-based tokenization
    return encoder

# ============================================
# HELPER FIXTURES
# ============================================

@pytest.fixture
def token_counter():
    """Real tiktoken counter for accurate tests"""
    import tiktoken
    enc = tiktoken.get_encoding("cl100k_base")
    return lambda text: len(enc.encode(text))

@pytest.fixture
def temp_results_dir(tmp_path):
    """Temporary directory for test results"""
    results_dir = tmp_path / "results"
    results_dir.mkdir()
    return results_dir

# ============================================
# MARKERS
# ============================================

def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "benchmark: marks tests as benchmarks")
    config.addinivalue_line("markers", "requires_api: marks tests that require real API keys")
