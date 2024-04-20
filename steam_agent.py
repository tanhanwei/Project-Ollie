import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.protobuf.struct_pb2 import Struct
import google.ai.generativelanguage as glm
import requests
import steamreviews
import json
from colors import print_blue, print_green, print_red, print_yellow

# Load the environment variables from the .env file
load_dotenv()

# Configure the API with your API key stored in an environment variable
genai.configure(api_key=os.environ["API_KEY"])


# Define a function to get appID from Steam API
def get_steam_appid(game_name):
    """Fetches the appID for a specified game name from Steam's API."""
    url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
    response = requests.get(url)
    if response.status_code == 200:
        apps = response.json()['applist']['apps']
        for app in apps:
            if game_name.lower() == app['name'].lower():
                return app['appid']
    return None

def extract_reviews_data(json_data):
    """
    Simplifies the extraction of review details from the provided JSON structure, focusing on essential attributes.
    
    :param json_data: The JSON data returned by the Steam reviews API.
    :return: A dictionary with a simple structure containing review details and a summary.
    """
    reviews_details = []
    reviews = json_data.get('reviews', {})

    for review in reviews.values():
        reviews_details.append({
            'review': review.get('review'),
        })

    summary = json_data.get('query_summary', {})

    return {
        'reviews_details': reviews_details,
        'summary': {
            'review_score_desc': summary.get('review_score_desc'),
            'total_positive': summary.get('total_positive'),
            'total_negative': summary.get('total_negative'),
            'total_reviews': summary.get('total_reviews')
        }
    }

def analyze_reviews(instruction: str, reviews_file_path: str):
    """
    Analyze reviews. You can summarize, perform sentiment analysis,
    or identify emerging topics.

    Args:
        instruction (str): Instructions for analysis, e.g., "Summarize these posts:", 
                           "Perform sentiment analysis for these posts:", or "Identify emerging topics for these posts:"

    Returns:
        str: Summary or analysis results, or a message indicating that no posts are available.
    """
    print("Starting analysis...")
    try:
        print(f"Loading file from {reviews_file_path}")
        with open(reviews_file_path, 'r', encoding='utf-8') as file:
            reviews_data = json.load(file)
        reviews_details = reviews_data.get('reviews_details', [])
        print(f"REVIEW DETAILS:\n{reviews_data}")
        if not reviews_details:
            return "No reviews data available for analysis."
        
        review_texts = [f"Review: {review['review']}" for review in reviews_details]
        print(f"review_text:\n{review_texts}")
        analysis_prompt = f"{instruction}\n\n{' '.join(review_texts)}"
        print(f"ANALYSIS PROMPT:\n\n{analysis_prompt}")
        
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        response = model.generate_content(analysis_prompt)
        print(f"ANALYSIS RESPONSE:\n{response.text}")
        
        # Save the post summary to a JSON file
        with open(f"{output_folder}/response.json", 'w') as file:
            json.dump(response.text, file)
        global task_completed
        task_completed = True
        return response.text
    except Exception as e:
        print(f"An error occurred: {e}")
        return str(e)

# Create the output folder if it doesn't exist
output_folder = "output/steam_agent"
os.makedirs(output_folder, exist_ok=True)

# Main interaction
# user_input = input("Enter the game name you are interested in: ")

# Use Gemini API to refine or confirm the game name
def retrieve_reviews(game_name: str):
    """Retrieve game reviews based on game name.

    Args:
        game_name: the game's name
    """
    basic_model = genai.GenerativeModel('gemini-1.0-pro-latest')
    response = basic_model.generate_content(f"Clarify this game title: {game_name} and respond with the game title only.")
    clarified_game_name = response.text.strip()
    print("Gemini suggests the game name might be:", clarified_game_name)

    # Fetch the appID for the clarified game name
    app_id = get_steam_appid(clarified_game_name)
    if app_id:
        print(f"Found appID for '{clarified_game_name}': {app_id}")

        # Download reviews for the appID
        request_params = dict()
        request_params['filter'] = 'all'
        request_params['day_range'] = '1'
        review_dict, query_count = steamreviews.download_reviews_for_app_id(app_id, chosen_request_params=request_params)

        # Process the downloaded reviews
        extracted_data = extract_reviews_data(review_dict)
        output_path = f"{output_folder}/{app_id}_reviews_extracted.json"

        # Save the raw reviews as a JSON file
        with open(f"{output_folder}/{app_id}_reviews_raw.json", 'w', encoding='utf-8') as f:
            json.dump(review_dict, f, ensure_ascii=False, indent=4)

        # Save the extracted reviews as a JSON file
        with open(f"{output_folder}/{app_id}_reviews_extracted.json", 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, ensure_ascii=False, indent=4)

        print(f"Reviews downloaded and processed. Raw data saved to '{output_folder}/{app_id}_reviews_raw.json'.")
        print(f"Extracted review details saved to '{output_folder}/{app_id}_reviews_extracted.json'.")
        # Perform analysis on the saved reviews
        # analysis_result = analyze_reviews(f"Summarize these reviews for the game called {clarified_game_name}:", output_path)
        # print("Analyzed.")
        return f"Reviews downloaded, processed and saved to '{output_folder}/{app_id}_reviews_extracted.json'."
    else:
        print(f"No matching Steam game found for '{clarified_game_name}'.")

# Create a dictionary of functions
functions = {
    'retrieve_reviews': retrieve_reviews,
    'analyze_reviews': analyze_reviews
}

# Initialize the Gemini model
model = genai.GenerativeModel(model_name='gemini-1.0-pro', tools=functions.values())
task_completed = False

def execute_function_sequence(model, functions, prompt):
    print(f"Executing function with the following prompt:\n\n {prompt}")
    messages = [{'role': 'user', 'parts': [{'text': prompt}]}]
    while not task_completed:
        print_blue(f"Message History:\n\n {messages}")
        response = model.generate_content(messages)
        print_yellow(f"AGENT RESPONSE: \n\n {response}")
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'function_call'):
                function_call = part.function_call
                if function_call.args is None:
                    print("Function call has no arguments.")
                    continue
                result = call_function(function_call, functions)
                
                s = Struct()
                s.update({'result': result})
                function_response = glm.Part(
                    function_response=glm.FunctionResponse(name=function_call.name, response=s))
                
                messages.append({'role': 'model', 'parts': [part]})
                messages.append({'role': 'user', 'parts': [function_response]})
            else:
                return getattr(part, 'text', 'No text available')
    return messages

def call_function(function_call, functions):
    function_name = function_call.name
    if function_call.args is None:
        print(f"No arguments passed to function {function_name}")
        return "Error: No arguments provided"
    function_args = {k: v for k, v in function_call.args.items()}
    return functions[function_name](**function_args)

def generate_response(prompt):
    prompt = f"""
        Based on user input, identify game name, retrieve game review, and analyze the result.

        User: {prompt}
    """
    result = execute_function_sequence(model, functions, prompt)

    # DEBUG
    print(result)

    return "Done with review analysis."

generate_response("Tell me more about gta5")