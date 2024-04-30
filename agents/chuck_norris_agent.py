# chuck_norris_agent.py
import os
from dotenv import load_dotenv
from agents.agent_base import AgentBase
import google.generativeai as genai
from utils.file import File
from app_constants import RESPONSE
import requests

load_dotenv()
output_folder = "output/chuck_norris_agent"
os.makedirs(output_folder, exist_ok=True)
response_path = f"{output_folder}/{RESPONSE}"

class ChuckNorrisAgent(AgentBase):
    description = "An agent that interacts with the Chuck Norris API to retrieve and present Chuck Norris facts."

    def __init__(self):
        self.data_store = {}
        self.functions = self.get_functions()
        super().__init__()
        self.model = genai.GenerativeModel(model_name='gemini-1.0-pro', tools=self.functions.values())
        self.chat = self.model.start_chat(enable_automatic_function_calling=True)

    def get_functions(self):
        return {
            'get_random_chuck_norris_joke': self.get_random_chuck_norris_joke,
            'get_chuck_norris_joke_by_category': self.get_chuck_norris_joke_by_category,
            'get_chuck_norris_joke_categories': self.get_chuck_norris_joke_categories,
            'search_chuck_norris_jokes': self.search_chuck_norris_jokes,
        }

    def get_random_chuck_norris_joke(self) -> str:
        """
        Retrieves a random Chuck Norris joke from the API.

        Returns:
            str: A random Chuck Norris joke.
        """
        response = requests.get("https://api.chucknorris.io/jokes/random")
        response.raise_for_status()
        joke_data = response.json()
        return joke_data['value']

    def get_chuck_norris_joke_by_category(self, category: str) -> str:
        """
        Retrieves a random Chuck Norris joke from a specific category.

        Args:
            category (str): The category of the joke.

        Returns:
            str: A Chuck Norris joke from the specified category.
        """
        response = requests.get(f"https://api.chucknorris.io/jokes/random?category={category}")
        response.raise_for_status()
        joke_data = response.json()
        return joke_data['value']

    def get_chuck_norris_joke_categories(self) -> list:
        """
        Retrieves a list of available Chuck Norris joke categories.

        Returns:
            list: A list of Chuck Norris joke categories.
        """
        response = requests.get("https://api.chucknorris.io/jokes/categories")
        response.raise_for_status()
        return response.json()

    def search_chuck_norris_jokes(self, query: str) -> list:
        """
        Searches for Chuck Norris jokes based on a search query.

        Args:
            query (str): The search query.

        Returns:
            list: A list of Chuck Norris jokes matching the search query.
        """
        response = requests.get(f"https://api.chucknorris.io/jokes/search?query={query}")
        response.raise_for_status()
        results = response.json()
        return [result['value'] for result in results['result']]

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
                Based on user input, perform the required tasks.

                User: {prompt}
            """
        result = self.execute_function_sequence(self.model, self.functions, prompt, self.chat)

        # Save the response or data to a file if needed
        File.write_md(result, response_path)

        return result
