from google.genai import types
import google.genai as genai
import config

class GenerativeModelWrapper:
    def __init__(self, model_name, system_instruction=None, safety_settings=None, tools=None):
        self.client = genai.Client(api_key=config.API_KEY)
        self.model_id = model_name
        self.system_instruction = system_instruction
        self.safety_settings = None # Ensure no old-style lists cause 'values' errors
        self.tools = tools

    def _prepare_tools(self, tools_input):
        """
        Converts any tool input (function, list, or dict) into 
        the specific [types.Tool(function_declarations=[...])] format.
        """
        if not tools_input:
            return None
            
        # FIX: If input is the function object, execute it to get the list
        if callable(tools_input):
            try:
                raw_list = tools_input()
            except Exception:
                raw_list = []
        else:
            raw_list = tools_input

        # Ensure we have a list to iterate over
        if not isinstance(raw_list, list):
            raw_list = [raw_list] if raw_list else []

        decls = []
        for t in raw_list:
            if isinstance(t, dict):
                # Ensure parameters is a dict to satisfy SDK mapping expectations
                params = t.get("parameters")
                if not isinstance(params, dict):
                    params = {"type": "OBJECT", "properties": {}}
                
                decls.append(types.FunctionDeclaration(
                    name=t.get("name"),
                    description=t.get("description", ""),
                    parameters=params
                ))
            elif hasattr(t, 'name'): 
                decls.append(t)
        
        if not decls:
            return None

        # Wrap in the list[types.Tool] structure required by the 2026 SDK
        return [types.Tool(function_declarations=decls)]

    def generate_content(self, conversation_history, tools=None):
        # Flatten history if nested
        if conversation_history and isinstance(conversation_history[0], list):
            conversation_history = conversation_history[0]

        formatted_history = []
        for turn in conversation_history:
            if not isinstance(turn, dict): continue
            role = turn.get('role', 'user')
            parts = turn.get('parts', [])
            
            clean_parts = []
            for p in parts:
                if isinstance(p, str):
                    clean_parts.append(types.Part.from_text(text=p))
                elif isinstance(p, dict):
                    if 'text' in p:
                        clean_parts.append(types.Part.from_text(text=p['text']))
                    elif 'function_call' in p:
                        clean_parts.append(types.Part(function_call=types.FunctionCall(
                            name=p['function_call']['name'], args=p['function_call']['args']
                        )))
                    elif 'function_response' in p:
                        clean_parts.append(types.Part(function_response=types.FunctionResponse(
                            name=p['function_response']['name'], response=p['function_response']['response']
                        )))
            formatted_history.append(types.Content(role=role, parts=clean_parts))

        # Explicitly prepare tools by checking for callables
        sdk_tools = self._prepare_tools(tools or self.tools)

        return self.client.models.generate_content(
            model=self.model_id,
            contents=formatted_history,
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                tools=sdk_tools
            )
        )

    def count_tokens(self, text):
        return self.client.models.count_tokens(model=self.model_id, contents=text)