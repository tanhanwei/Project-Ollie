# web_scrapper_agent.py
import os
from dotenv import load_dotenv
from agents.agent_base import AgentBase
import google.generativeai as genai
from utils.file import File
from app_constants import RESPONSE
from newspaper import Article

load_dotenv()
output_folder = "output/web_scrapper_agent"
os.makedirs(output_folder, exist_ok=True)
response_path = f"{output_folder}/{RESPONSE}"

class WebScrapperAgent(AgentBase):
    description = "A web scrapper agent that extracts article content from given URLs."

    def __init__(self):
        self.data_store = {}
        self.functions = self.get_functions()
        super().__init__()
        self.model = genai.GenerativeModel(model_name='gemini-1.0-pro', tools=self.functions.values())
        self.chat = self.model.start_chat(enable_automatic_function_calling=True)

    def get_functions(self):
        return {
            'extract_article_content': self.extract_article_content,
            # Add more functions as needed
        }

    def extract_article_content(self, url: str) -> str:
        """
        Extracts the content of an article from a given URL.

        Args:
            url (str): The URL of the article.

        Returns:
            str: The extracted article content.
        """
        article = Article(url)
        article.download()
        article.parse()
        result = article.text
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
                Based on user input, perform the required tasks.

                User: {prompt}
            """
        result = self.execute_function_sequence(self.model, self.functions, prompt, self.chat)

        # Save the response or data to a file if needed
        File.write_md(result, response_path)

        return result