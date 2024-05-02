```python
# g_{agent_name}_agent.py
import os
from dotenv import load_dotenv
from agents.agent_base import AgentBase
import google.generativeai as genai
from utils.file import File
from app_constants import RESPONSE

load_dotenv()
output_folder = f"output/{__name__.split('.')[-1]}"
os.makedirs(output_folder, exist_ok=True)
response_path = f"{output_folder}/{RESPONSE}"

class {AgentName}Agent(AgentBase):
    description = "A brief description of what the {AgentName}Agent does."

    def __init__(self):
        self.data_store = {}
        self.functions = self.get_functions()
        super().__init__()

    def get_functions(self):
        return {
            'function_name_1': self.function_name_1,
            'function_name_2': self.function_name_2,
            # Add more functions as needed
        }

    def function_name_1(self, arg1: str, arg2: int) -> str:
        """
        A brief description of what function_name_1 does.

        Args:
            arg1 (str): Description of arg1. Example: "example value".
            arg2 (int): Description of arg2. Example: 42.

        Returns:
            str: Description of the return value.
        """
        self.emit_debug_message(f"{AGENT NAME}: {agent describing what it's trying to do}", "{AGENT NAME}")    
        # Function implementation goes here
        result = "Function 1 result"
        return result

    def function_name_2(self, arg1: list) -> dict:
        """
        A brief description of what function_name_2 does.

        Args:
            arg1 (list): Description of arg1. Example: ["item1", "item2"].

        Returns:
            dict: Description of the return value.
        """
        self.emit_debug_message(f"{AGENT NAME}: {agent describing what it's trying to do}", "{AGENT NAME}")   
        # Function implementation goes here
        result = {"key": "value"}
        return result

    def generate_response(self, prompt: str) -> str:
        """
        Generate a response based on the user's prompt.

        Args:
            prompt (str): The user's prompt.

        Returns:
            str: The generated response.
        """
        if self.first_conversation:
            prompt = f"""
                {Insert details prompt here to specify the agents name, identity, and capabilities}
                
                Example: You are the {agent name}, you can {capabilities}.
        
                Based on user input, perform the required tasks.

                User: {prompt}
            """
        result = self.execute_function_sequence(self.model, self.functions, prompt, self.chat)

        # Save the response or data to a file if needed
        File.write_md(result, response_path)

        return result
```

# Explanation of the template:

1. The `NewAgent` class inherits from `AgentBase`, ensuring that it has access to the common functionality provided by the base class.

2. The `description` class variable provides a brief description of what the agent does.

3. The `__init__` method calls the parent class constructor using `super().__init__()`.

4. The `get_functions` method returns a dictionary mapping function names to their corresponding method references. This allows the functions to be called by the Gemini API.

5. Each function that can be called by the Gemini API (`function_name_1` and `function_name_2` in this example) has a descriptive docstring that includes:
   - A brief description of what the function does.
   - `Args`: The input arguments, their types, and example values.
   - `Returns`: A description of the return value.

6. The functions that can be called by the Gemini API are included in the `get_functions` method.

7. The `generate_response` method takes a `prompt` as input and generates a response using the `execute_function_sequence` method provided by `AgentBase`. It returns the response as a string.

8. Optionally, the agent can save long results, data, or responses to a file in the `output/{agent_name}/response.md` format.

9. Naming convention must be {something}_agent.py. For example: youtube_agent, recipe_agent, etc.

10. All data MUST be saved externally. Any local data variable such as self.data, self.data_store, etc must be saved externally.

11. Function sequence can be chained so that the final response gives the final answer or summary.