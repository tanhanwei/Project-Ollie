import os
import requests
from newspaper import Article
import json
from dotenv import load_dotenv
from agents.agent_base import AgentBase
import google.generativeai as genai

load_dotenv()
output_folder = "output/web_search_agent"
os.makedirs(output_folder, exist_ok=True)

class WebSearchAgent(AgentBase):
    def __init__(self):
        super().__init__()
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        self.api_key = os.getenv("BRAVE_SEARCH_API_KEY")  # Load API key from .env file
        self.headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key
        }
        self.data_store = {}
        self.functions = {
            'search_web': self.search_web,
            'process_search_results': self.process_search_results,
            'extract_relevant_content': self.extract_relevant_content,
            'summarize_content': self.summarize_content
        }
        self.model = genai.GenerativeModel(model_name='gemini-1.0-pro', tools=self.functions.values())
        self.chat = self.model.start_chat(enable_automatic_function_calling=True)

    def search_web(self, search_query: str, num_results: int = 10):
        """
        Perform a web search using the Brave Search API.

        Args:
            search_query (str): The search query.
            num_results (int): The number of search results to retrieve (default: 10).

        Returns:
            str: Status of the search operation.
        """
        print(f"WEB SEARCH AGENT: Searching the web with: '{search_query} with max {num_results} results.")
        params = {
            "q": search_query,
            "count": num_results
        }

        try:
            response = requests.get(self.base_url, params=params, headers=self.headers)
            print(f"WEB SEARCH AGENT DEBUG: RESPONSE: \n\n{response}")
            response.raise_for_status()
            search_data = response.json()

            if "web" in search_data and "results" in search_data["web"]:
                search_results = search_data["web"]["results"]
                self.data_store["search_results"] = search_results
                return f"Found {len(search_results)} search results."
            else:
                return "No search results found."

        except requests.exceptions.RequestException as e:
            return f"Error occurred while making the request to Brave Search API: {str(e)}"

    def process_search_results(self, search_query: str):
        """
        Process the search results and select the most relevant ones.

        Args:
            search_query (str): The original search query.

        Returns:
            str: Status of the search result processing.
        """
        search_results = self.data_store.get("search_results", [])
        if not search_results:
            return "No search results found for processing."

        titles = [result["title"] for result in search_results]
        relevance_prompt = f"""
        Based on the following search result titles:

        {titles}

        Please select the most relevant titles for the search query: '{search_query}'.
        Return your response in the following JSON format:
        {{
            "relevant_indices": [<index1>, <index2>, ...]
        }}
        """
        relevance_response = self.pro_generate_analysis(relevance_prompt, output_folder)
        response_text = json.loads(relevance_response)["response"]
        relevant_indices = json.loads(response_text)["relevant_indices"]

        relevant_results = [search_results[index] for index in relevant_indices]
        self.data_store["relevant_results"] = relevant_results

        return f"Selected {len(relevant_results)} relevant search results."

    def extract_relevant_content(self):
        """
        Extract relevant content from the selected search results.

        Returns:
            str: Status of the content extraction.
        """
        relevant_results = self.data_store.get("relevant_results", [])
        if not relevant_results:
            return "No relevant results found for content extraction."

        extracted_content = []
        for index, result in enumerate(relevant_results):
            url = result["url"]

            try:
                article = Article(url)
                article.download()
                article.parse()

                main_content = article.text
                extracted_content.append(main_content)

                output_file = f"{output_folder}/result_{index}.txt"
                with open(output_file, "w", encoding="utf-8") as file:
                    file.write(main_content)

            except Exception as e:
                print(f"Error processing URL: {url}")
                print(f"Error message: {str(e)}")

        self.data_store["extracted_content"] = extracted_content
        return f"Extracted content from {len(extracted_content)} search results."

    def summarize_content(self):
        """
        Summarize the extracted content.

        Returns:
            str: Status of the content summarization.
        """
        extracted_content = self.data_store.get("extracted_content", [])
        if not extracted_content:
            return "No extracted content found for summarization."

        summaries = []
        for index, content in enumerate(extracted_content):
            summary_prompt = f"""
            Please summarize the following text:

            {content}
            """
            summary_response = self.pro_generate_analysis(summary_prompt, output_folder)
            summary = json.loads(summary_response)["response"]
            summaries.append(summary)

            summary_file = f"{output_folder}/summary_{index}.txt"
            with open(summary_file, "w", encoding="utf-8") as file:
                file.write(summary)

        self.data_store["summaries"] = summaries
        return f"Generated summaries for {len(summaries)} content pieces."

    def generate_response(self, prompt):
        prompt = f"""
            Based on user input, perform a web search, process the search results, extract relevant content, and summarize the content.

            User: {prompt}
        """
        result = self.execute_function_sequence(self.model, self.functions, prompt, self.chat)

        return "Done with web search and content summarization."