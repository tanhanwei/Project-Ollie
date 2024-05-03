# wikipedia_agent.py
import os
from dotenv import load_dotenv
from agents.agent_base import AgentBase
import google.generativeai as genai
from utils.file import File
from app_constants import RESPONSE
import wikipedia

load_dotenv()
output_folder = f"output/{__name__.split('.')[-1]}"
response_path = f"{output_folder}/{RESPONSE}"

class WikipediaAgent(AgentBase):
    description = "A Wikipedia Agent that can search and summarize information from Wikipedia."

    def __init__(self):
        self.data_store = {}
        self.functions = self.get_functions()
        super().__init__()
        os.makedirs(output_folder, exist_ok=True)

    def get_functions(self):
        return {
            'search_wikipedia': self.search_wikipedia,
            'summarize_wikipedia': self.summarize_wikipedia,
        }

    def search_wikipedia(self, query: str) -> list:
        """
        Searches Wikipedia for a given query and returns a list of relevant page titles.

        Args:
            query (str): The search query.

        Returns:
            list: A list of relevant Wikipedia page titles.
        """
        self.emit_debug_message(f"WikipediaAgent: Searching Wikipedia for '{query}'", "WikipediaAgent")
        search_results = wikipedia.search(query)
        return search_results

    def summarize_wikipedia(self, page_title: str) -> str:
        """
        Summarizes a Wikipedia page for a given page title.

        Args:
            page_title (str): The title of the Wikipedia page to summarize.

        Returns:
            str: A summary of the Wikipedia page.
        """
        self.emit_debug_message(f"WikipediaAgent: Summarizing Wikipedia page '{page_title}'", "WikipediaAgent")
        try:
            wikipedia_page = wikipedia.page(page_title)
            summary = wikipedia_page.summary
        except wikipedia.exceptions.PageError:
            summary = f"Error: Page '{page_title}' not found on Wikipedia."
        except wikipedia.exceptions.DisambiguationError as e:
            summary = f"Error: Disambiguation page found for '{page_title}'. Please specify one of the following options:\n{e.options}"
        return summary

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
                You are the Wikipedia Agent, you can search and summarize information from Wikipedia.
        
                Based on user input, perform the required tasks.

                User: {prompt}
            """
        result = self.execute_function_sequence(self.model, self.functions, prompt, self.chat)

        # Save the response or data to a file if needed
        File.write_md(result, response_path)

        return result