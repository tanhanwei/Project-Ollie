import requests
from newspaper import Article
import json
from llm_api import call_google_llm_api

# Brave Search API endpoint
base_url = "https://api.search.brave.com/res/v1/web/search"

# Your Brave Search API key
api_key = "BSA7ILe807-3l133jECvGwkVYlr5q4l"

# Search query and parameters
search_query = "top open world game in 2024"
num_results = 10
params = {
    "q": search_query,
    "count": num_results
}

# Request headers
headers = {
    "Accept": "application/json",
    "Accept-Encoding": "gzip",
    "X-Subscription-Token": api_key
}

try:
    # Send request to Brave Search API
    response = requests.get(base_url, params=params, headers=headers)
    response.raise_for_status()
    search_data = response.json()

    # Process search results
    if "web" in search_data and "results" in search_data["web"]:
        search_results = search_data["web"]["results"]

        print(f"No. of RESULT: {len(search_results)}")
        print("SEARCH RESULT:")
        print(json.dumps(search_results, indent=4))

        # Extract the titles from the search results
        titles = [result["title"] for result in search_results]

        # Prompt the LLM to decide which search results are relevant based on titles
        relevance_prompt = f"""
        Based on the following search result titles:

        {titles}

        Please select the most relevant titles for the search query: '{search_query}'.
        Return your response in the following JSON format:
        {{
            "relevant_indices": [<index1>, <index2>, ...]
        }}
        """
        relevance_response = call_google_llm_api(relevance_prompt)
        response_text = json.loads(relevance_response)["response"]
        relevant_indices = json.loads(response_text)["relevant_indices"]

        print("Relevant Results:")
        for index in relevant_indices:
            print(json.dumps(search_results[index], indent=4))

        for index in relevant_indices:
            url = search_results[index]["url"]

            try:
                article = Article(url)
                article.download()
                article.parse()

                main_content = article.text

                output_file = f"result_{index}.txt"
                with open(output_file, "w", encoding="utf-8") as file:
                    file.write(main_content)

                print(f"Content saved to {output_file}.")

                # Prompt the LLM to summarize the extracted text
                summary_prompt = f"""
                Please summarize the following text:

                {main_content}
                """
                summary_response = call_google_llm_api(summary_prompt)
                summary = json.loads(summary_response)["response"]

                summary_file = f"summary_{index}.txt"
                with open(summary_file, "w", encoding="utf-8") as file:
                    file.write(summary)

                print(f"Summary saved to {summary_file}.")

            except Exception as e:
                print(f"Error processing URL: {url}")
                print(f"Error message: {str(e)}")
    else:
        print("No search results found.")

except requests.exceptions.RequestException as e:
    print("Error occurred while making the request to Brave Search API.")
    print(f"Error message: {str(e)}")