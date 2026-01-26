import unittest
from unittest.mock import MagicMock
import agent.core
from agent.main import handle_agent_task

class TestAgentIntegration(unittest.TestCase):
    def test_run_agent_step_signature_match(self):
        """
        Verifies that agent.core.run_agent_step can be called with the arguments
        used in agent.main, and returns the expected 3 values.
        """
        # Mock models
        mock_model = MagicMock()
        # Mock generate_content return
        mock_response = MagicMock()
        mock_response.candidates = [MagicMock()]
        part = MagicMock(text="Mock thought")
        part.function_call = None
        mock_response.candidates[0].content.parts = [part]
        mock_model.generate_content.return_value = mock_response

        models = {"main": mock_model}
        history = []
        user_id = "test_user"

        # Test Case 1: Initial call (no user_input)
        # agent.main calls: done, response, last_user_input = run_agent_step(models, history, user_id, print_func=print)
        done, response, last_user_input = agent.core.run_agent_step(
            models, history, user_id, print_func=lambda x: None
        )

        self.assertTrue(done) # Should be True if no tool call
        self.assertEqual(response, "Mock thought")
        self.assertEqual(last_user_input, "") # No user input in this turn

        # Test Case 2: Loop call (with user_input)
        # agent.main calls: done, response, last_user_input = run_agent_step(models, history, user_id, user_input=user_input, print_func=print)
        user_input = "Hello agent"
        done, response, last_user_input = agent.core.run_agent_step(
            models, history, user_id, user_input=user_input, print_func=lambda x: None
        )

        self.assertTrue(done)
        self.assertEqual(response, "Mock thought")
        self.assertEqual(last_user_input, "Hello agent")
        self.assertEqual(history[-2]['parts'][0], "Hello agent") # Verify history update

    def test_tool_execution_flow(self):
        """
        Verifies that if the model returns a function call, run_agent_step returns done=False
        and updates history with the function response.
        """
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_candidate = MagicMock()

        # Simulate a function call part
        part_fc = MagicMock()
        part_fc.text = "I will run a tool."
        part_fc.function_call.name = "test_tool"
        part_fc.function_call.args = {"arg": "val"}

        mock_candidate.content.parts = [part_fc]
        mock_response.candidates = [mock_candidate]
        mock_model.generate_content.return_value = mock_response

        models = {"main": mock_model}
        history = []

        # We need to mock tools_mod.execute_tool to avoid actual execution errors
        original_execute_tool = agent.core.execute_tool
        agent.core.execute_tool = MagicMock(return_value="Tool output")

        try:
            done, response, last_user_input = agent.core.run_agent_step(
                models, history, "user", user_input="Run tool", print_func=lambda x: None
            )

            self.assertFalse(done) # Should be False because tool executed
            self.assertIn("Tool output", str(history[-1])) # Check history for result
            self.assertEqual(response, "I will run a tool.")

        finally:
            agent.core.execute_tool = original_execute_tool

if __name__ == "__main__":
    unittest.main()
