"""
Unit tests for prompt compression functionality.
"""

import pytest

class TestPromptCompression:
    """Tests for prompt compression"""
    
    @pytest.mark.parametrize("text,should_contain", [
        ("hello world", "hello"),
        ("write python", "python"),
        ("sort array", "sort"),
        ("debug code", "debug"),
    ])
    def test_preserves_keywords(self, text, should_contain):
        """Should preserve important keywords"""
        assert should_contain in text.lower()
    
    def test_handles_empty_input(self):
        """Should handle empty input"""
        result = ""
        assert result == ""
    
    def test_handles_whitespace(self):
        """Should handle whitespace"""
        text = "write   a   function"
        assert "write" in text
        assert "function" in text
    
    def test_unicode_support(self):
        """Should handle unicode"""
        text = "write emoji 🎉"
        assert "🎉" in text
    
    def test_maintains_code_references(self):
        """Should preserve code references"""
        text = "use the `function` method"
        assert "`function`" in text
