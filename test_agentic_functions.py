import unittest
from unittest.mock import MagicMock, patch
from api import agentic_reason_and_act
from tools_mod import tool_definitions

class TestAgenticWorkflow(unittest.TestCase):

    def setUp(self):
        """Set up a mock model and basic inputs for the tests."""
        # Create a mock for the GenerativeModel
        self.mock_model = MagicMock()

        # Define a sample conversation history
        self.conversation_history = [
            {"role": "user", "parts": ["What is the current directory?"]},
        ]

        # Get the tool definitions
        self.tools = list(tool_definitions.values())

    def test_agent_produces_thought_and_tool_call(self):
        """
        Verify that the agent can produce a thought and a corresponding tool call.
        """
        # Configure the mock model to return a response with a function call
        mock_response = MagicMock()
        mock_function_call = MagicMock()
        mock_function_call.name = "execute_shell_command"
        mock_function_call.args = {"command": "ls"}

        mock_response.parts = [
            MagicMock(
                function_call=mock_function_call,
                text="I should use the shell to find the current directory."
            )
        ]
        self.mock_model.generate_content.return_value = mock_response

        # Call the function with the mocked model
        thought, function_call = agentic_reason_and_act(
            self.mock_model, self.conversation_history, self.tools
        )

        # 1. Assert that a thought was produced
        self.assertIn("I should use the shell", thought)

        # 2. Assert that a function call was returned
        self.assertIsNotNone(function_call)
        self.assertEqual(function_call.name, "execute_shell_command")
        self.assertIn("ls", function_call.args["command"])

        # 3. Verify that the model's generate_content was called correctly
        self.mock_model.generate_content.assert_called_once_with(
            self.conversation_history, tools=self.tools
        )

    def test_agent_produces_final_response_without_tool_call(self):
        """
        Verify that the agent can produce a final response when no tool is needed.
        """
        # Configure the mock model to return a text-only response
        mock_response = MagicMock()
        mock_response.parts = [
            MagicMock(function_call=None, text="Hello! I am ready to assist you.")
        ]
        self.mock_model.generate_content.return_value = mock_response

        # Call the function with the mocked model
        thought, function_call = agentic_reason_and_act(
            self.mock_model, self.conversation_history, self.tools
        )

        # 1. Assert that the thought contains the final response
        self.assertIn("Hello!", thought)

        # 2. Assert that no function call was returned
        self.assertIsNone(function_call)

        # 3. Verify that the model's generate_content was called correctly
        self.mock_model.generate_content.assert_called_once_with(
            self.conversation_history, tools=self.tools
        )

if __name__ == "__main__":
    unittest.main()
