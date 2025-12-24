import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mock the genai library
sys.modules["google.generativeai"] = MagicMock()

from api import agentic_reason_and_act
from tools_mod import tool_definitions


class TestAgent(unittest.TestCase):

    def test_agentic_reason_and_act_with_text(self):
        # Mock the Gemini API call to return a text response
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.parts = [MagicMock()]
        mock_response.parts[0].text = "mocked thought"
        mock_response.parts[0].function_call = None
        mock_model.generate_content.return_value = mock_response

        # Test agentic_reason_and_act
        prompt = "test prompt"
        tools = list(tool_definitions.values())
        thought, function_call = agentic_reason_and_act(
            mock_model, [{"role": "user", "parts": [prompt]}], tools
        )
        self.assertEqual(thought, "mocked thought")
        self.assertIsNone(function_call)

    def test_agentic_reason_and_act_with_function_call(self):
        # Mock the Gemini API call to return a function call
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_function_call = MagicMock()
        mock_function_call.name = "google_search"
        mock_function_call.args = {"query": "test"}
        mock_response.parts = [MagicMock()]
        mock_response.parts[0].text = "I should search for test"
        mock_response.parts[0].function_call = mock_function_call
        mock_model.generate_content.return_value = mock_response

        # Test agentic_reason_and_act
        prompt = "test prompt"
        tools = list(tool_definitions.values())
        thought, function_call = agentic_reason_and_act(
            mock_model, [{"role": "user", "parts": [prompt]}], tools
        )
        self.assertEqual(thought, "I should search for test")
        self.assertIsNotNone(function_call)
        self.assertEqual(function_call.name, "google_search")
        self.assertEqual(function_call.args["query"], "test")


if __name__ == "__main__":
    unittest.main()
