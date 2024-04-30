# new_agent.py
import os
from agents.agent_base import AgentBase

output_folder = "output/new_agent"
os.makedirs(output_folder, exist_ok=True)

class NewAgent(AgentBase):
    description = "A brief description of what the NewAgent does."

    def __init__(self):
        self.functions = self.get_functions() 
        super().__init__()

    def get_functions(self):
        return {
            'function_name_1': self.function_name_1,
            'function_name_2': self.function_name_2
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
        # Function implementation goes here
        result = {"key": "value"}
        return result

    def generate_response(self, prompt: str) -> str:
        # Generate a response based on the prompt
        response = self.execute_function_sequence(self.model, self.functions, prompt, self.chat)

        # Optionally, save the response or data to a file
        # with open("output/new_agent/response.json", "w") as file:
        #     file.write(response)

        return response