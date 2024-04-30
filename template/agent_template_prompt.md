Please create an Web Search Agent Class based on the template and my old code:

# Template

```python
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
```

Explanation of the template:

1. The `NewAgent` class inherits from `AgentBase`, ensuring that it has access to the common functionality provided by the base class.

2. The `description` class variable provides a brief description of what the agent does.

3. The `__init__` method calls the parent class constructor using `super().__init__()`.

4. The `get_functions` method returns a dictionary mapping function names to their corresponding method references. This allows the functions to be called by the Gemini API.

5. Each function that can be called by the Gemini API (`function_name_1` and `function_name_2` in this example) has a descriptive docstring that includes:
   - A brief description of what the function does.
   - `Args`: The input arguments, their types, and example values.
   - `Returns`: A description of the return value.

6. The functions that can be called by the Gemini API are included in the `get_functions` method.

7. The `generate_response` method takes a `prompt` as input and generates a response using the `execute_function_sequence` method provided by `AgentBase`. It returns the response as a string.

8. Optionally, the agent can save long results, data, or responses to a file in the `output/{agent_name}/response.json` format.

9. Naming convention must be {something}_agent.py. For example: youtube_agent, recipe_agent, etc.

10. All data MUST be saved externally. Any local data variable such as self.data, self.data_store, etc must be saved externally.

11. Function sequence can be chained so that the final response gives the final answer or summary.

# Old Code:


```python
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

    def extract_relevant_content(self):
        """
        Extract relevant content from the selected search results.

        Returns:
            str: Status of the content extraction.
        """
        relevant_results = self.data_store.get("relevant_results", [])
        if not relevant_results:
            return "No relevant results found for content extraction."
        
        # TODO: Change to this after filter functino is 
        # relevant_results = self.data_store.get("relevant_results", [])
        # if not relevant_results:
        #     return "No relevant results found for content extraction."

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
```
