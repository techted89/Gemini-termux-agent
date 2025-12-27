import google.genai as genai
import config

class GenerativeModelWrapper:
    def __init__(self, model_name, safety_settings=None, tools=None):
        self.client = genai.Client(api_key=config.API_KEY)
        self.model = self.client.models.get(f"models/{model_name}")
        self.safety_settings = safety_settings
        self.tools = tools

    def generate_content(self, conversation_history, tools=None):
        # The new API uses the client to generate content.
        # We'll need to adapt the conversation history format if it's different.
        # Assuming the new format is similar for now.
        response = self.client.models.generate_content(
            model=self.model.name,
            contents=conversation_history,
            safety_settings=self.safety_settings,
            tools=tools or self.tools,
        )
        return response
