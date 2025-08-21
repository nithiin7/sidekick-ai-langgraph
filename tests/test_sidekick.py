"""
Tests for the Sidekick core functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from src.core.sidekick import Sidekick
from src.core.state import State, create_initial_state


class TestSidekick:
    """Test cases for the Sidekick class."""
    
    @pytest.fixture
    def sidekick(self):
        """Create a Sidekick instance for testing."""
        return Sidekick()
    
    @pytest.fixture
    def mock_state(self):
        """Create a mock state for testing."""
        return create_initial_state("test message", "test criteria")
    
    def test_sidekick_initialization(self, sidekick):
        """Test Sidekick initialization."""
        assert sidekick.sidekick_id is not None
        assert sidekick._is_initialized is False
        assert sidekick.tools is None
        assert sidekick.graph is None
    
    def test_create_initial_state(self):
        """Test initial state creation."""
        state = create_initial_state("test message", "test criteria")
        
        assert state["messages"] == "test message"
        assert state["success_criteria"] == "test criteria"
        assert state["feedback_on_work"] is None
        assert state["success_criteria_met"] is False
        assert state["user_input_needed"] is False
    
    def test_create_initial_state_default_criteria(self):
        """Test initial state creation with default success criteria."""
        state = create_initial_state("test message", "")
        
        assert state["success_criteria"] == "The answer should be clear and accurate"
    
    @pytest.mark.asyncio
    async def test_setup_failure(self, sidekick):
        """Test setup failure handling."""
        with patch('src.core.sidekick.playwright_tools', side_effect=Exception("Setup failed")):
            with pytest.raises(RuntimeError, match="Failed to setup Sidekick"):
                await sidekick.setup()
    
    def test_worker_router_with_tools(self, sidekick):
        """Test worker router with tool calls."""
        mock_message = Mock()
        mock_message.tool_calls = ["tool1", "tool2"]
        
        state = {"messages": [mock_message]}
        result = sidekick.worker_router(state)
        
        assert result == "tools"
    
    def test_worker_router_without_tools(self, sidekick):
        """Test worker router without tool calls."""
        mock_message = Mock()
        mock_message.tool_calls = None
        
        state = {"messages": [mock_message]}
        result = sidekick.worker_router(state)
        
        assert result == "evaluator"
    
    def test_route_based_on_evaluation_success(self, sidekick):
        """Test evaluation routing when success criteria is met."""
        state = {
            "success_criteria_met": True,
            "user_input_needed": False
        }
        
        result = sidekick.route_based_on_evaluation(state)
        assert result == "END"
    
    def test_route_based_on_evaluation_user_input_needed(self, sidekick):
        """Test evaluation routing when user input is needed."""
        state = {
            "success_criteria_met": False,
            "user_input_needed": True
        }
        
        result = sidekick.route_based_on_evaluation(state)
        assert result == "END"
    
    def test_route_based_on_evaluation_continue(self, sidekick):
        """Test evaluation routing when work should continue."""
        state = {
            "success_criteria_met": False,
            "user_input_needed": False
        }
        
        result = sidekick.route_based_on_evaluation(state)
        assert result == "worker"
    
    @pytest.mark.asyncio
    async def test_run_superstep_not_initialized(self, sidekick):
        """Test running superstep without initialization."""
        with pytest.raises(RuntimeError, match="Sidekick not initialized"):
            await sidekick.run_superstep("test", "criteria", [])
    
    @pytest.mark.asyncio
    async def test_cleanup(self, sidekick):
        """Test cleanup functionality."""
        # Mock browser and playwright
        sidekick.browser = Mock()
        sidekick.playwright = Mock()
        sidekick._is_initialized = True
        
        await sidekick.cleanup()
        
        assert sidekick.browser is None
        assert sidekick.playwright is None
        assert sidekick._is_initialized is False


if __name__ == "__main__":
    pytest.main([__file__])
