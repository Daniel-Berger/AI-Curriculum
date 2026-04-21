"""
Tests for AI Agent

Unit tests for agent functionality, tool execution, and error handling.
"""

import unittest
from unittest.mock import patch, MagicMock
from agent import run_agent, execute_tools, extract_text_response
from tools import calculator, get_current_time


class TestToolExecution(unittest.TestCase):
    """Test individual tool functions."""

    def test_calculator_basic(self):
        """Test basic arithmetic."""
        result = calculator("2 + 3")
        self.assertEqual(result, "5")

    def test_calculator_complex(self):
        """Test complex expression."""
        result = calculator("10 * 5 + 3")
        self.assertEqual(result, "53")

    def test_calculator_error(self):
        """Test invalid expression."""
        result = calculator("invalid")
        self.assertIn("error", result.lower() or isinstance(result, str))

    def test_get_current_time(self):
        """Test time function returns string."""
        result = get_current_time()
        self.assertIsInstance(result, str)
        self.assertIn("-", result)  # Should have date format


class TestToolBlockExecution(unittest.TestCase):
    """Test execution of tool_use blocks."""

    def test_execute_single_tool(self):
        """Test executing a single tool_use block."""
        # Mock tool_use block
        mock_block = MagicMock()
        mock_block.type = 'tool_use'
        mock_block.name = 'calculator'
        mock_block.input = {'expression': '2 + 2'}
        mock_block.id = 'tool_123'

        results = execute_tools([mock_block])

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['tool_use_id'], 'tool_123')
        self.assertIn('4', results[0]['content'])

    def test_execute_tool_not_found(self):
        """Test error handling for non-existent tool."""
        mock_block = MagicMock()
        mock_block.type = 'tool_use'
        mock_block.name = 'nonexistent_tool'
        mock_block.input = {}
        mock_block.id = 'tool_456'

        results = execute_tools([mock_block])

        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]['is_error'])
        self.assertIn('not found', results[0]['content'].lower())

    def test_skip_non_tool_blocks(self):
        """Test that non-tool blocks are skipped."""
        mock_text = MagicMock()
        mock_text.type = 'text'

        results = execute_tools([mock_text])
        self.assertEqual(len(results), 0)


class TestResponseExtraction(unittest.TestCase):
    """Test extracting responses from content blocks."""

    def test_extract_text_response(self):
        """Test extracting text from content blocks."""
        mock_block = MagicMock()
        mock_block.type = 'text'
        mock_block.text = 'The answer is 42'

        result = extract_text_response([mock_block])
        self.assertEqual(result, 'The answer is 42')

    def test_extract_empty_response(self):
        """Test handling empty response."""
        result = extract_text_response([])
        self.assertEqual(result, "")

    def test_extract_multiple_blocks(self):
        """Test extracting from multiple blocks returns first text."""
        mock_block1 = MagicMock()
        mock_block1.type = 'text'
        mock_block1.text = 'First'

        mock_block2 = MagicMock()
        mock_block2.type = 'text'
        mock_block2.text = 'Second'

        result = extract_text_response([mock_block1, mock_block2])
        self.assertEqual(result, 'First')


class TestAgentIntegration(unittest.TestCase):
    """Integration tests for the agent."""

    @patch('agent.anthropic.Anthropic')
    def test_agent_simple_response(self, mock_anthropic):
        """Test agent with simple text response (no tools)."""
        # Mock Claude response with just text
        mock_text_block = MagicMock()
        mock_text_block.type = 'text'
        mock_text_block.text = 'The answer is 150'

        mock_response = MagicMock()
        mock_response.stop_reason = 'end_turn'
        mock_response.content = [mock_text_block]

        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        # Run agent
        result = run_agent("What is 100 + 50?")

        self.assertEqual(result, 'The answer is 150')
        mock_client.messages.create.assert_called_once()

    @patch('agent.anthropic.Anthropic')
    def test_agent_with_tool_use(self, mock_anthropic):
        """Test agent that uses a tool then responds."""
        mock_client = MagicMock()

        # First response: tool use
        mock_tool_block = MagicMock()
        mock_tool_block.type = 'tool_use'
        mock_tool_block.name = 'calculator'
        mock_tool_block.input = {'expression': '100 + 50'}
        mock_tool_block.id = 'tool_123'

        mock_response_1 = MagicMock()
        mock_response_1.stop_reason = 'tool_use'
        mock_response_1.content = [mock_tool_block]

        # Second response: final answer
        mock_text_block = MagicMock()
        mock_text_block.type = 'text'
        mock_text_block.text = 'The result is 150'

        mock_response_2 = MagicMock()
        mock_response_2.stop_reason = 'end_turn'
        mock_response_2.content = [mock_text_block]

        # Set up side effects
        mock_client.messages.create.side_effect = [mock_response_1, mock_response_2]
        mock_anthropic.return_value = mock_client

        # Run agent
        result = run_agent("What is 100 + 50?")

        self.assertEqual(result, 'The result is 150')
        # Should be called twice: once for tool, once for final answer
        self.assertEqual(mock_client.messages.create.call_count, 2)

    @patch('agent.anthropic.Anthropic')
    def test_agent_max_iterations(self, mock_anthropic):
        """Test agent respects max_iterations."""
        mock_client = MagicMock()

        # Always return tool use (no final answer)
        mock_tool_block = MagicMock()
        mock_tool_block.type = 'tool_use'
        mock_tool_block.name = 'calculator'
        mock_tool_block.input = {'expression': '1 + 1'}
        mock_tool_block.id = 'tool_123'

        mock_response = MagicMock()
        mock_response.stop_reason = 'tool_use'
        mock_response.content = [mock_tool_block]

        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        # Run with max 2 iterations
        result = run_agent("Test query", max_iterations=2)

        self.assertIn("Maximum iterations", result)
        # Called max_iterations times
        self.assertEqual(mock_client.messages.create.call_count, 2)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""

    def test_calculator_empty_expression(self):
        """Test calculator with empty expression."""
        result = calculator("")
        self.assertIn("error", result.lower() or isinstance(result, str))

    def test_execute_tool_input_error(self):
        """Test tool execution with wrong input type."""
        mock_block = MagicMock()
        mock_block.type = 'tool_use'
        mock_block.name = 'calculator'
        mock_block.input = {'expression': 123}  # Wrong type
        mock_block.id = 'tool_err'

        results = execute_tools([mock_block])

        self.assertTrue(results[0]['is_error'])

    @patch('agent.anthropic.Anthropic')
    def test_agent_handles_api_error(self, mock_anthropic):
        """Test agent handles API errors gracefully."""
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = Exception("API Error")
        mock_anthropic.return_value = mock_client

        # Should raise or handle gracefully
        try:
            run_agent("Test")
            self.fail("Should have raised exception")
        except Exception as e:
            self.assertIn("API Error", str(e))


def run_tests():
    """Run all tests."""
    unittest.main(verbosity=2)


if __name__ == '__main__':
    run_tests()
