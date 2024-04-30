# chuck_norris_agent.py
import os
import requests
from agents.agent_base import AgentBase
import json

output_folder = "output/chuck_norris_agent"
os.makedirs(output_folder, exist_ok=True)

class ChuckNorrisAgent(AgentBase):
    description = "An agent that retrieves Chuck Norris facts using the chucknorris.io API."

    def __init__(self):
        self.functions = self.get_functions() 
        super().__init__()

    def get_functions(self):
        return {
            'get_random_fact': self.get_random_fact,
            'get_fact_from_category': self.get_fact_from_category,
            'search_facts': self.search_facts
        }

    def get_random_fact(self) -> str:
        url = "https://api.chucknorris.io/jokes/random"
        response = requests.get(url)
        try:
            data = response.json()
            return data["value"]
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Raw response content: {response.text}")
            return "Error occurred while parsing the response."
        
    def get_fact_from_category(self, category: str) -> str:
        url = f"https://api.chucknorris.io/jokes/random?category={category}"
        response = requests.get(url)
        if response.status_code == 404:
            print(f"Category '{category}' not found. Fallback to default category.")
            url = "https://api.chucknorris.io/jokes/random"
            response = requests.get(url)
        try:
            data = response.json()
            return data["value"]
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error occurred while parsing the response: {e}")
            print(f"Raw response content: {response.text}")
            return "Error occurred while retrieving the fact."

    def search_facts(self, query: str) -> list:
        url = f"https://api.chucknorris.io/jokes/search?query={query}"
        response = requests.get(url)
        try:
            data = response.json()
            facts = [item["value"] for item in data["result"]]
            return facts
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Raw response content: {response.text}")
            return []

    def generate_response(self, prompt: str) -> str:
        # Generate a response based on the prompt
        response = self.execute_function_sequence(self.model, self.functions, prompt, self.chat)
        
        if isinstance(response, str):
            return response
        else:
            print(f"Unexpected response format: {type(response)}")
            return "Unexpected response format."