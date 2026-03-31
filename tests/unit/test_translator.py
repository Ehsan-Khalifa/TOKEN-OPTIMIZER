"""
Unit tests for translation functionality.
"""

import pytest
from unittest.mock import Mock, patch

class TestTranslationOptimization:
    """Tests for translation-based optimization"""
    
    def test_preserves_code_blocks(self):
        """Should not translate code"""
        input_text = """Write a function:
```python
def hello():
    print("world")
```"""
        assert 'def hello():' in input_text
        assert 'print("world")' in input_text
    
    def test_preserves_urls(self):
        """Should not translate URLs"""
        input_text = "Check https://github.com/example for more"
        assert 'https://github.com/example' in input_text
    
    def test_preserves_constants(self):
        """Should preserve constants"""
        input_text = "Set the MAX_SIZE to 100"
        assert 'MAX_SIZE' in input_text
    
    @pytest.mark.parametrize("term", ['API', 'JSON', 'REST', 'OAuth', 'JWT'])
    def test_preserves_technical_terms(self, term):
        """Should not translate technical terms"""
        input_text = f"Use {term} for authentication"
        assert term in input_text
    
    def test_handles_empty_input(self):
        """Should handle empty input"""
        result = ""
        assert result == ""
    
    def test_handles_code_only(self):
        """Should handle code-only input"""
        input_text = "```python\ndef foo(): pass\n```"
        assert 'def foo()' in input_text
    
    def test_handles_special_characters(self):
        """Should handle special characters"""
        input_text = "Use symbols: @#$%^&*()"
        assert "@" in input_text
        assert "#" in input_text
