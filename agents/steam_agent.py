import os
from dotenv import load_dotenv
import google.generativeai as genai
import requests
import steamreviews
import json
from agents.agent_base import AgentBase

load_dotenv()
genai.configure(api_key=os.environ["API_KEY"])
output_folder = "output/steam_agent"
os.makedirs(output_folder, exist_ok=True)

class SteamAgent(AgentBase):
    description = "An agent that can retrieve game reviews by specifying game name and analyse them."
    def __init__(self):
        super().__init__()
        # self.delegate_docstring = """
        # Delegate the task to the steam agent.
        
        # Args:
        #     query: instruction for steam agent to analyze a game. Must include a game's name.
        # Returns:
        #     str: the status of the analysis.
        # """
        self.functions = {
            'retrieve_reviews': self.retrieve_reviews,
            'analyze_reviews': self.analyze_reviews
        }
        self.model = genai.GenerativeModel(model_name='gemini-1.0-pro', tools=self.functions.values())
        self.chat = self.model.start_chat(enable_automatic_function_calling=True)

    def get_steam_appid(self, game_name):
        url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
        response = requests.get(url)
        if response.status_code == 200:
            apps = response.json()['applist']['apps']
            for app in apps:
                if game_name.lower() == app['name'].lower():
                    return app['appid']
        return None

    def extract_reviews_data(self, json_data):
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

    def analyze_reviews(self, instruction: str, reviews_file_path: str):
        """
        Analyze reviews. You can summarize, perform sentiment analysis,
        or identify emerging topics.

        Args:
            instruction (str): Instructions for analysis, e.g., "Summarize these posts:", 
                            "Perform sentiment analysis for these posts:", or "Identify emerging topics for these posts:"

        Returns:
            str: Summary or analysis results, or a message indicating that no posts are available.
        """
        print("STEAM AGENT: ANALYSING REVIEWS")
        try:
            with open(reviews_file_path, 'r', encoding='utf-8') as file:
                reviews_data = json.load(file)
            reviews_details = reviews_data.get('reviews_details', [])
            if not reviews_details:
                return "No reviews data available for analysis."

            review_texts = [f"Review: {review['review']}" for review in reviews_details]
            analysis_prompt = f"{instruction}\n\n{' '.join(review_texts)}"

            response = self.pro_generate_analysis(analysis_prompt,output_folder)

            return f"Review analysis has been completed and is saved in '{output_folder}'"

        except Exception as e:
            return str(e)

    def retrieve_reviews(self, game_name: str):
        """
        Retrieve game reviews based on game_name.

        Args:
            game_name: the name of the game

        Returns:
            str: Status of the retrieval.
        """
        basic_model = genai.GenerativeModel('gemini-1.0-pro-latest')
        response = basic_model.generate_content(f"Clarify this game title: {game_name} and respond with the game title only.")
        clarified_game_name = response.text.strip()
        print("STEAM AGENT: Got it, looking for game reviews for ", clarified_game_name)

        app_id = self.get_steam_appid(clarified_game_name)
        if app_id:
            print(f"Found appID for '{clarified_game_name}': {app_id}")

            request_params = dict()
            request_params['filter'] = 'all'
            request_params['day_range'] = '1'
            review_dict, query_count = steamreviews.download_reviews_for_app_id(app_id, chosen_request_params=request_params)

            extracted_data = self.extract_reviews_data(review_dict)
            output_path = f"{output_folder}/{app_id}_reviews_extracted.json"

            with open(f"{output_folder}/{app_id}_reviews_raw.json", 'w', encoding='utf-8') as f:
                json.dump(review_dict, f, ensure_ascii=False, indent=4)

            with open(f"{output_folder}/{app_id}_reviews_extracted.json", 'w', encoding='utf-8') as f:
                json.dump(extracted_data, f, ensure_ascii=False, indent=4)

            print(f"STEAM AGENT: Reviews downloaded and processed. Raw data saved to '{output_folder}/{app_id}_reviews_raw.json'.")
            print(f"STEAM AGENT: Extracted review details saved to '{output_folder}/{app_id}_reviews_extracted.json'.")
            return f"Reviews downloaded, processed and saved to '{output_folder}/{app_id}_reviews_extracted.json'."
        else:
            print(f"STEAM AGENT: Whoops, no matching Steam game found for '{clarified_game_name}'.")

    def generate_response(self, prompt):
        prompt = f"""
            Based on user input, identify game name, retrieve game review, and analyze the result.

            User: {prompt}
        """
        response = self.execute_function_sequence(self.model, self.functions, prompt, self.chat)

        return response