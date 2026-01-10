import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mock the genai library
sys.modules["google.genai"] = MagicMock()

from api import agentic_reason_and_act
from tools_mod import get_all_tool_definitions


class TestAgent(unittest.TestCase):

    def test_agentic_reason_and_act_with_text(self):
        # Mock the Gemini API call to return a text response
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_candidate = MagicMock()
        mock_content = MagicMock()
        mock_part = MagicMock()
        mock_part.text = "mocked thought"
        mock_part.function_call = None
        mock_content.parts = [mock_part]
        mock_candidate.content = mock_content
        mock_response.candidates = [mock_candidate]
        mock_model.generate_content.return_value = mock_response

        # Test agentic_reason_and_act
        prompt = "test prompt"
        tools = get_all_tool_definitions()
        thought, function_call = agentic_reason_and_act(
            mock_model, [{"role": "user", "parts": [prompt]}], tools
        )
        self.assertEqual(thought, "mocked thought")
        self.assertIsNone(function_call)

    def test_agentic_reason_and_act_with_function_call(self):
        # Mock the Gemini API call to return a function call
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_candidate = MagicMock()
        mock_content = MagicMock()
        mock_part = MagicMock()
        mock_function_call = MagicMock()
        mock_function_call.name = "google_search"
        mock_function_call.args = {"query": "test"}
        mock_part.text = "I should search for test"
        mock_part.function_call = mock_function_call
        mock_content.parts = [mock_part]
        mock_candidate.content = mock_content
        mock_response.candidates = [mock_candidate]
        mock_model.generate_content.return_value = mock_response

        # Test agentic_reason_and_act
        prompt = "test prompt"
        tools = get_all_tool_definitions()
        thought, function_call = agentic_reason_and_act(
            mock_model, [{"role": "user", "parts": [prompt]}], tools
        )
        self.assertEqual(thought, "I should search for test")
        self.assertIsNotNone(function_call)
        self.assertEqual(function_call.name, "google_search")
        self.assertEqual(function_call.args["query"], "test")


if __name__ == "__main__":
    unittest.main()
