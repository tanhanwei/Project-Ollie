# web_search_agent.py
import os
import requests
from newspaper import Article
import json
from dotenv import load_dotenv
from agents.agent_base import AgentBase
import google.generativeai as genai
from utils.file import File
from app_constants import RESPONSE, RESPONSE_STYLE

load_dotenv()
output_folder = f"output/{__name__.split('.')[-1]}"
os.makedirs(output_folder, exist_ok=True)
response_path = f"{output_folder}/{RESPONSE}"

class WebSearchAgent(AgentBase):
    description = "An agent that performs web searches, processes search results, extracts relevant content, and summarizes the content."

    def __init__(self):
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        self.api_key = os.getenv("BRAVE_SEARCH_API_KEY")  # Load API key from .env file
        self.headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key
        }
        self.data_store = {}
        self.functions = self.get_functions()
        super().__init__()
        self.model = genai.GenerativeModel(model_name='gemini-1.0-pro', tools=self.functions.values())
        self.chat = self.model.start_chat(enable_automatic_function_calling=True)

    def get_functions(self):
        return {
            'search_web': self.search_web,
            #'process_search_results': self.process_search_results,
            # 'extract_relevant_content': self.extract_relevant_content,
            # 'summarize_content': self.summarize_content
            'search_extract_summarize': self.search_extract_summarize
        }
    
    def search_extract_summarize(self, search_query: str, num_results: int = 10) -> str:
        self.search_web(search_query, num_results)
        if self.data_store["search_results"]:
            self.extract_relevant_content()
            if self.data_store["extracted_content"]:
                response = self.summarize_content()
                return response
            else:
                return "WEB SEARCH AGENT: No data extracted"
        else:
            return "WEB SEARCH AGENT: No relevant search results"


    def search_web(self, search_query: str, num_results: int = 10) -> str:
        """
        Perform a web search using the Brave Search API.

        Args:
            search_query (str): The search query. Use only relevant keywords".
            num_results (int): The number of search results to retrieve (default: 10).

        Returns:
            str: Status of the search operation.
        """
        print(f"WEB SEARCH AGENT: Searching the web with: '{search_query}' with max {num_results} results.")
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
                # return f"Found {len(search_results)} search results."
                print(f"Found {len(search_results)} search results.")
            else:
                return "No search results found."

        except requests.exceptions.RequestException as e:
            return f"Error occurred while making the request to Brave Search API: {str(e)}"

    def extract_relevant_content(self) -> str:
        """
        Extract relevant content from the selected search results.

        Returns:
            str: Status of the content extraction.
        """
        print("WEB SEARCH AGENT: Extracting content...")
        # relevant_results = self.data_store.get("relevant_results", [])
        relevant_results = self.data_store.get("search_results", [])
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
                print("WEB SEARCH AGENT: Saved to output folder")

            except Exception as e:
                print(f"Error processing URL: {url}")
                print(f"Error message: {str(e)}")
        print("WEB SEARCH AGENT: Saving extracted content")
        self.data_store["extracted_content"] = extracted_content
        # return f"Extracted content from {len(extracted_content)} search results."
        print(f"WEB SEARCH AGENT: Extracted content from {len(extracted_content)} search results.")


    def summarize_content(self) -> str:
        """
        Summarize the extracted content.

        Returns:
            str: Status of the content summarization.
        """
        print("WEB SEARCH AGENT: Summarising content")
        extracted_content = self.data_store.get("extracted_content", [])
        if not extracted_content:
            return "No extracted content found for summarization."

        combined_content = "\n".join(extracted_content)
        
        summary_prompt = f"""
        Please analyse and summarize the following web content and write an article.
        
        {RESPONSE_STYLE}

        {combined_content}
        """

        print(f"SUMMARY PROMPT:\n\n{summary_prompt}")
        summary = self.pro_generate_analysis(summary_prompt)
        # summary = json.loads(summary_response)["response"]

        # summary_data = {
        #     "summary": summary,
        #     "content": combined_content
        # }

        # summary_file = f"{output_folder}/response.json"
        # with open(summary_file, "w", encoding="utf-8") as file:
        #     json.dump(summary_data, file, indent=4)

        self.data_store["summary"] = summary
        File.write_md(summary, response_path)

        return f"Generated summary and saved to {response_path}"

    def generate_response(self, prompt: str) -> str:
        if self.first_conversation:
            prompt = f"""
                Based on user input, perform a web search, extract relevant content, and summarize the content.

                User: {prompt}
                
            """
        result = self.execute_function_sequence(self.model, self.functions, prompt, self.chat)

        # with open(f"{output_folder}/response.json", "w") as file:
        #     json.dump(self.data_store, file)
        

        return result