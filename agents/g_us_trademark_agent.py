# g_us_trademark_agent.py
# Gemini's Explanation:
# Here is a brief explanation of the code:

# 1. The `generate_and_save_code` function takes the agent name as input and generates the full Python code for the agent.
# 2. The `UsTrademarkAgent` class inherits from the `AgentBase` class and implements the following functions:
#     - `serial_number_search`: Searches for a trademark by its serial number and returns the registration data.
#     - `trademark_search`: Searches for trademarks matching the given search term and status.
#     - `description_search`: Searches for trademarks with descriptions matching the given search term and status.
#     - `owner_search`: Searches for trademarks owned by entities matching the given search term.
#     - `expiration_search`: Searches for trademarks expiring within the specified time frame.
# 3. The `generate_response` function generates a response based on the user's prompt. It first checks if this is the first conversation with the user, and if so, it adds a prefix to the prompt to explain that the agent is using the Marker API V2 to perform the tasks. It then executes the appropriate function sequence based on the user's prompt and saves the response or data to a file if needed.

# You can now use the `UsTrademarkAgent` class to perform trademark searches and retrievals using the Marker API V2.

import os
from dotenv import load_dotenv
from agents.agent_base import AgentBase
import google.generativeai as genai
from utils.file import File
from app_constants import RESPONSE

load_dotenv()
output_folder = f"output/{__name__.split('.')[-1]}"
response_path = f"{output_folder}/{RESPONSE}"

class UsTrademarkAgent(AgentBase):
    description = "A US Trademark Agent that interacts with the Marker API V2 to perform trademark searches and retrievals."

    def __init__(self):
        self.data_store = {}
        self.functions = self.get_functions()
        super().__init__()
        os.makedirs(output_folder, exist_ok=True)

    def get_functions(self):
        return {
            'serial_number_search': self.serial_number_search,
            'trademark_search': self.trademark_search,
            'description_search': self.description_search,
            'owner_search': self.owner_search,
            'expiration_search': self.expiration_search,
        }

    def serial_number_search(self, serial_number: str) -> dict:
        """
        Searches for a trademark by its serial number and returns the registration data.

        Args:
            serial_number (str): The serial number of the trademark to search for.

        Returns:
            dict: A dictionary containing the trademark registration data, or an empty dictionary if not found.
        """
        # Function implementation goes here (using the Marker API)
        print("Performing serial number search...")
        # ...
        result = {"key": "value"}  # Replace with actual API response
        return result

    def trademark_search(self, search_term: str, status: str = "active", start: int = 1) -> list:
        """
        Searches for trademarks matching the given search term and status.

        Args:
            search_term (str): The term to search for (can include wildcards).
            status (str, optional): The status of trademarks to return ("active" or "all"). Defaults to "active".
            start (int, optional): The starting page number for results (used for pagination). Defaults to 1.

        Returns:
            list: A list of dictionaries, each containing trademark data for matching trademarks.
        """
        # Function implementation goes here (using the Marker API)
        print("Performing trademark search...")
        # ...
        result = [{"key": "value"}]  # Replace with actual API response
        return result

    def description_search(self, search_term: str, status: str = "active", start: int = 1) -> list:
        """
        Searches for trademarks with descriptions matching the given search term and status.

        Args:
            search_term (str): The term to search for within trademark descriptions.
            status (str, optional): The status of trademarks to return ("active" or "all"). Defaults to "active".
            start (int, optional): The starting page number for results (used for pagination). Defaults to 1.

        Returns:
            list: A list of dictionaries, each containing trademark data for matching trademarks.
        """
        # Function implementation goes here (using the Marker API)
        print("Performing description search...")
        # ...
        result = [{"key": "value"}]  # Replace with actual API response
        return result

    def owner_search(self, search_term: str, start: int = 1) -> list:
        """
        Searches for trademarks owned by entities matching the given search term.

        Args:
            search_term (str): The term to search for within trademark owner names (can include wildcards).
            start (int, optional): The starting page number for results (used for pagination). Defaults to 1.

        Returns:
            list: A list of dictionaries, each containing trademark data for matching trademarks.
        """
        # Function implementation goes here (using the Marker API)
        print("Performing owner search...")
        # ...
        result = [{"key": "value"}]  # Replace with actual API response
        return result

    def expiration_search(self, time_frame: str, start: int = 1) -> list:
        """
        Searches for trademarks expiring within the specified time frame.

        Args:
            time_frame (str): The time frame for expiration, e.g., "6 months", "1 year", "90 days".
            start (int, optional): The starting page number for results (used for pagination). Defaults to 1.

        Returns:
            list: A list of dictionaries, each containing trademark data for matching trademarks.
        """
        # Function implementation goes here (using the Marker API)
        print("Performing expiration search...")
        # ...
        result = [{"key": "value"}]  # Replace with actual API response
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
                Based on user input, perform the required tasks using the Marker API V2.

                User: {prompt}
            """
        result = self.execute_function_sequence(self.model, self.functions, prompt, self.chat)

        # Save the response or data to a file if needed
        File.write_md(result, response_path)

        return result