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
os.makedirs(output_folder, exist_ok=True)
response_path = f"{output_folder}/{RESPONSE}"

class WikipediaAgent(AgentBase):
    description = "A versatile Wikipedia agent capable of retrieving summaries, searching for pages, and providing related information."

    def __init__(self):
        self.data_store = {}
        self.functions = self.get_functions()
        super().__init__()

    def get_functions(self):
        return {
            'get_summary': self.get_summary,
            'search_wikipedia': self.search_wikipedia,
            'get_page_links': self.get_page_links,
            'get_page_categories': self.get_page_categories,
        }

    def get_summary(self, topic: str, sentences: int = 2) -> str:
        """
        Retrieves a concise summary of a given topic from Wikipedia.

        Args:
            topic (str): The topic to summarize. Example: "Albert Einstein".
            sentences (int, optional): The number of sentences in the summary. Defaults to 2.

        Returns:
            str: The summarized content from Wikipedia.
        """
        try:
            print("WIKI AGENT: Attempting to get summary")
            summary = wikipedia.summary(topic, sentences=sentences)
            return summary
        except wikipedia.exceptions.DisambiguationError as e:
            return f"Multiple options found for '{topic}'. Please be more specific."
        except wikipedia.exceptions.PageError:
            return f"No Wikipedia page found for '{topic}'."

    def search_wikipedia(self, query: str) -> list:
        """
        Searches Wikipedia for pages related to the given query.

        Args:
            query (str): The search query. Example: "artificial intelligence".

        Returns:
            list: A list of page titles matching the query.
        """
        results = wikipedia.search(query)
        return results

    def get_page_links(self, page_title: str) -> list:
        """
        Retrieves a list of links from a given Wikipedia page.

        Args:
            page_title (str): The title of the Wikipedia page. Example: "Python (programming language)".

        Returns:
            list: A list of link titles from the page.
        """
        try:
            page = wikipedia.page(page_title)
            links = list(page.links)
            return links
        except wikipedia.exceptions.DisambiguationError as e:
            return f"Multiple options found for '{page_title}'. Please be more specific."
        except wikipedia.exceptions.PageError:
            return f"No Wikipedia page found for '{page_title}'."

    def get_page_categories(self, page_title: str) -> list:
        """
        Retrieves a list of categories associated with a given Wikipedia page.

        Args:
            page_title (str): The title of the Wikipedia page. Example: "Machine learning". 

        Returns:
            list: A list of category names associated with the page. 
        """
        try:
            page = wikipedia.page(page_title)
            categories = list(page.categories)
            return categories
        except wikipedia.exceptions.DisambiguationError as e:
            return f"Multiple options found for '{page_title}'. Please be more specific."
        except wikipedia.exceptions.PageError:
            return f"No Wikipedia page found for '{page_title}'."

    def generate_response(self, prompt: str) -> str:
        """
        Generate a response based on the user's prompt.

        Args:
            prompt (str): The user's prompt.

        Returns:
            str: The generated response.
        """
        print("WIKI AGENT: Attempting to generate a response...")
        if self.first_conversation:
            prompt = f"""
                Based on user input, perform the required tasks.

                User: {prompt}
            """
        result = self.execute_function_sequence(self.model, self.functions, prompt, self.chat)

        # Save the response or data to a file if needed
        File.write_md(result, response_path)

        return result