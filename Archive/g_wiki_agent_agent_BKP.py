# wikipedia_agent.py
import os
from dotenv import load_dotenv
from agents.agent_base import AgentBase
import google.generativeai as genai
from utils.file import File
from app_constants import RESPONSE
import wikipedia

load_dotenv()
output_folder = "output/wikipedia_agent"
os.makedirs(output_folder, exist_ok=True)
response_path = f"{output_folder}/{RESPONSE}"

class WikipediaAgent(AgentBase):
    description = "A brief description of what the WikipediaAgent does."

    def __init__(self):
        self.data_store = {}
        self.functions = self.get_functions()
        super().__init__()
        self.model = genai.GenerativeModel(model_name='gemini-1.0-pro', tools=self.functions.values())
        self.chat = self.model.start_chat(enable_automatic_function_calling=True)

    def get_functions(self):
        return {
            'get_wikipedia_summary': self.get_wikipedia_summary,
            'get_wikipedia_page': self.get_wikipedia_page,
            # Add more functions as needed
        }

    def get_wikipedia_summary(self, topic: str, sentences: int = 2) -> str:
        """
        Get a summary of a Wikipedia topic.

        Args:
            topic (str): The topic to summarize. Example: "Albert Einstein".
            sentences (int): The number of sentences in the summary. Example: 2.

        Returns:
            str: The summary of the Wikipedia topic.
        """
        try:
            summary = wikipedia.summary(topic, sentences=sentences)
            return summary
        except wikipedia.exceptions.DisambiguationError as e:
            return f"Multiple options found for '{topic}'. Please be more specific."
        except wikipedia.exceptions.PageError as e:
            return f"No Wikipedia page found for '{topic}'."

    def get_wikipedia_page(self, topic: str) -> str:
        """
        Get the URL of a Wikipedia page.

        Args:
            topic (str): The topic to get the page for. Example: "Albert Einstein".

        Returns:
            str: The URL of the Wikipedia page.
        """
        try:
            page = wikipedia.page(topic)
            return page.url
        except wikipedia.exceptions.DisambiguationError as e:
            return f"Multiple options found for '{topic}'. Please be more specific."
        except wikipedia.exceptions.PageError as e:
            return f"No Wikipedia page found for '{topic}'."

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