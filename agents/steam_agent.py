import os
from dotenv import load_dotenv
import google.generativeai as genai
import requests
import steamreviews
import json
from agents.agent_base import AgentBase
from utils.file import File
from app_constants import RESPONSE, RESPONSE_STYLE

load_dotenv()
genai.configure(api_key=os.environ["API_KEY"])
output_folder = f"output/{__name__.split('.')[-1]}"
os.makedirs(output_folder, exist_ok=True)
response_path = f"{output_folder}/{RESPONSE}"

class SteamAgent(AgentBase):
    description = "An agent that can retrieve game reviews by specifying game name and analyse them."
    def __init__(self):
        self.functions = self.get_functions() 
        super().__init__()
    
    def get_functions(self):
        return {
            # 'retrieve_reviews': self.retrieve_reviews,
            # 'analyze_reviews': self.analyze_reviews,
            'retrieve_extract_and_analyze_reviews': self.retrieve_extract_and_analyze_reviews
        }

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
            instruction (str): Instructions for analysis, e.g., "Summarize these reviews:", 
                            "Perform sentiment analysis for these reviews:", or "Identify emerging topics for these game reviews:"

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
            # analysis_prompt = f"{instruction}\n\n{' '.join(review_texts)}"

            analysis_prompt = f"""
            {instruction}

            {RESPONSE_STYLE}

            Here are the reviews:

            {review_texts}
        """   

            analysis = self.pro_generate_analysis(analysis_prompt)

            File.write_md(analysis, response_path)

            return f"STEAM AGENT: Review analysis has been completed and is saved in '{response_path}'"

        except Exception as e:
            return str(e)
        
    def clarify_game_title(self, game_name):
        """
        Clarify game name as user might misspell or use accronymns
        """
        # using another model instance so it doesn't affect steam agent message history
        basic_model = genai.GenerativeModel('gemini-1.0-pro-latest')
        response = basic_model.generate_content(f"Clarify this game title: {game_name} and respond with the game title only.")
        clarified_game_name = response.text.strip()
        
        print("STEAM AGENT: Got it, looking for game reviews for ", clarified_game_name)
        
        return clarified_game_name

    def retrieve_reviews(self, game_name: str, day_range: int = 1):
        """
        Retrieve game reviews based on game_name.

        Args:
            game_name: the name of the game

        Returns:
            str: Status of the retrieval.
        """

        app_id = self.get_steam_appid(game_name)
        if app_id:
            print(f"Found appID for '{game_name}': {app_id}")

            request_params = dict()
            request_params['filter'] = 'all'
            request_params['day_range'] = f"{day_range}"
            review_dict, query_count = steamreviews.download_reviews_for_app_id(app_id, chosen_request_params=request_params)

            return app_id, review_dict
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
            print(f"STEAM AGENT: Whoops, no matching Steam game found for '{game_name}'.")

    def save_data(self, app_id, reviews, extracted_data):
        raw_review_path = f"{output_folder}/{app_id}_reviews_raw.json"
        extracted_review_path = f"{output_folder}/{app_id}_reviews_extracted.json"
        with open(raw_review_path, 'w', encoding='utf-8') as f:
            json.dump(reviews, f, ensure_ascii=False, indent=4)

        with open(extracted_review_path, 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, ensure_ascii=False, indent=4)
        
        return f"Review and extracted data saved to {output_folder}", extracted_review_path

    def retrieve_extract_and_analyze_reviews(self, game_name: str, instruction: str, day_range: int):
        """
            Retrieve, extract, and analyse game reviews

            Args:
                game_name: game name indicated by user
                instruction: Detailed and clear instruction for analyser to analyse the reviews. For example: "Perform sentiment analysis of the reviews and make a conclusion", "Find emerging topics and make a conclusion with key takeaways", etc.
                day_range: range of days of reviews. Default day range is 1, unless specified by user.
            Returns:
                str: analysis status
        """
        clarified_game_name = self.clarify_game_title(game_name)
        
        self.emit_debug_message(f"STEAM AGENT: Got it, retrieving reviews for {clarified_game_name}...", "STEAM AGENT")
        print(f"\nSTEAM AGENT: Looking for game reviews for {clarified_game_name} within day range of {day_range}.\n")
        app_id, reviews = self.retrieve_reviews(clarified_game_name, day_range)
        
        self.emit_debug_message(f"STEAM AGENT: Extracting important parts from the review data...", "STEAM AGENT")
        extracted_data = self.extract_reviews_data(reviews)
        
        status, extracted_data_path = self.save_data(app_id, reviews, extracted_data)
        
        print(status)

        self.emit_debug_message(f"STEAM AGENT: Analyzing the review data now...", "STEAM AGENT")
        response = self.analyze_reviews(instruction, extracted_data_path)

        self.emit_debug_message(f"STEAM AGENT: Done! Analysis saved in {response_path}", "STEAM AGENT")

        return response

    def generate_response(self, prompt):
        prompt = f"""
            Based on user input, identify game name, retrieve game review, and analyze the result.

            User: {prompt}
        """
        response = self.execute_function_sequence(self.model, self.functions, prompt, self.chat)

        return response