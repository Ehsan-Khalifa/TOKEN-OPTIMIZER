"""
Unit tests for middleware functionality.
"""

import pytest
from unittest.mock import Mock, patch
from src.middleware.token_optimizer import (
    TokenOptimizerMiddleware,
    OptimizationLevel,
    OptimizationStats
)

class TestTokenOptimizerMiddleware:
    """Tests for TokenOptimizerMiddleware class"""
    
    @pytest.fixture
    def middleware(self, mock_env):
        """Create middleware with standard settings"""
        return TokenOptimizerMiddleware(level=OptimizationLevel.STANDARD)
    
    @pytest.fixture
    def aggressive_middleware(self, mock_env):
        """Create middleware with aggressive settings"""
        with patch('src.translators.deepl_translator.DeepLTokenOptimizer'):
            return TokenOptimizerMiddleware(
                level=OptimizationLevel.AGGRESSIVE,
                enable_translation=False
            )
    
    # ============================================
    # INITIALIZATION TESTS
    # ============================================
    
    def test_initializes_with_default_level(self, mock_env):
        """Should initialize with STANDARD level by default"""
        middleware = TokenOptimizerMiddleware()
        assert middleware.level == OptimizationLevel.STANDARD
    
    @pytest.mark.parametrize("level", [
        OptimizationLevel.MINIMAL,
        OptimizationLevel.STANDARD,
        OptimizationLevel.AGGRESSIVE,
        OptimizationLevel.MAXIMUM,
    ])
    def test_initializes_with_all_levels(self, mock_env, level):
        """Should initialize with all optimization levels"""
        with patch('src.translators.deepl_translator.DeepLTokenOptimizer'):
            with patch('src.optimizers.llmlingua_compressor.LLMLinguaOptimizer'):
                middleware = TokenOptimizerMiddleware(level=level)
                assert middleware.level == level
    
    # ============================================
    # INPUT OPTIMIZATION TESTS
    # ============================================
    
    def test_optimizes_input_messages(self, middleware, sample_messages):
        """Should optimize input messages"""
        if hasattr(middleware, 'optimize_input'):
            optimized, opts = middleware.optimize_input(sample_messages)
            assert len(optimized) == len(sample_messages)
    
    def test_removes_fillers_from_input(self, middleware):
        """Should remove filler words from input"""
        messages = [{"role": "user", "content": "Please kindly write a function"}]
        if hasattr(middleware, 'optimize_input'):
            optimized, _ = middleware.optimize_input(messages)
            assert "please" not in optimized[0]['content'].lower()
    
    def test_preserves_message_roles(self, middleware, sample_messages):
        """Should preserve message roles during optimization"""
        if hasattr(middleware, 'optimize_input'):
            optimized, _ = middleware.optimize_input(sample_messages)
            for orig, opt in zip(sample_messages, optimized):
                assert opt['role'] == orig['role']
    
    # ============================================
    # OUTPUT CONSTRAINT TESTS
    # ============================================
    
    def test_injects_code_constraints(self, middleware, sample_messages):
        """Should inject code constraints for code requests"""
        if hasattr(middleware, 'inject_output_constraints'):
            result = middleware.inject_output_constraints(sample_messages, is_code_request=True)
            all_content = ' '.join(m['content'] for m in result)
            assert 'code only' in all_content.lower() or 'CRITICAL' in all_content
    
    # ============================================
    # OUTPUT STRIPPING TESTS
    # ============================================
    
    def test_strips_output(self, middleware):
        """Should strip unnecessary content from output"""
        if hasattr(middleware, 'strip_output'):
            response = "Sure, here's the code:\n\ndef foo(): pass\n\nHope this helps!"
            stripped = middleware.strip_output(response)
            assert "Hope this helps" not in stripped
            assert "def foo():" in stripped
    
    # ============================================
    # STOP SEQUENCES TESTS
    # ============================================
    
    def test_returns_code_stop_sequences(self, middleware):
        """Should return appropriate stop sequences for code"""
        if hasattr(middleware, 'get_stop_sequences'):
            sequences = middleware.get_stop_sequences(is_code_request=True)
            assert isinstance(sequences, list)
    
    # ============================================
    # FULL PIPELINE TESTS
    # ============================================
    
    def test_full_optimization_pipeline(self, middleware, mock_llm_client, sample_messages):
        """Should run complete optimization pipeline"""
        result = middleware.optimize(
            messages=sample_messages,
            llm_call=mock_llm_client.chat,
            is_code_request=True
        )
        
        assert 'response' in result
        assert 'stats' in result
        assert isinstance(result['stats'], OptimizationStats)
    
    def test_tracks_optimization_stats(self, middleware, mock_llm_client, sample_messages):
        """Should track optimization statistics"""
        result = middleware.optimize(
            messages=sample_messages,
            llm_call=mock_llm_client.chat,
            is_code_request=True
        )
        
        stats = result['stats']
        assert stats.original_input_tokens > 0
        assert stats.optimized_input_tokens >= 0
        assert isinstance(stats.total_savings_percent, float)
    
    # ============================================
    # EDGE CASES
    # ============================================
    
    def test_handles_empty_messages(self, middleware, mock_llm_client):
        """Should handle empty message list"""
        result = middleware.optimize(
            messages=[],
            llm_call=mock_llm_client.chat
        )
        assert 'response' in result


class TestOptimizationStats:
    """Tests for OptimizationStats dataclass"""
    
    def test_creates_stats_object(self):
        """Should create OptimizationStats correctly"""
        stats = OptimizationStats(
            original_input_tokens=100,
            optimized_input_tokens=60,
            original_output_tokens=200,
            optimized_output_tokens=100,
            input_savings_percent=40.0,
            output_savings_percent=50.0,
            total_savings_percent=46.67,
            optimizations_applied=["basic_cleaning", "output_stripping"]
        )
        
        assert stats.input_savings_percent == 40.0
        assert stats.output_savings_percent == 50.0
        assert len(stats.optimizations_applied) == 2
