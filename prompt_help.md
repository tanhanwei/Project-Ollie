Here are my old codes:
agent_base.py
```
from abc import ABC, abstractmethod
import google.generativeai as genai
from google.protobuf.struct_pb2 import Struct
import google.ai.generativelanguage as glm
import json

class AgentBase(ABC):
    def __init__(self):
        # self.model = genai.GenerativeModel(model_name='gemini-1.0-pro')
        self.task_completed = False
        self.messages = []

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        pass

    def execute_function_sequence(self, model, functions, prompt, chat):
        self.task_completed = False

        while not self.task_completed:
            print("Generating response...")
            response = chat.send_message(prompt)
            print(f"TASK COMPLETED: {self.task_completed}")
        return response.text
    
    def pro_generate_analysis(self, summary_prompt, output_folder):
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        response = model.generate_content(summary_prompt)
        print(response)
        
        try:
            response = model.generate_content(
                summary_prompt,
                safety_settings={
                    'HATE': 'BLOCK_NONE',
                    'HARASSMENT': 'BLOCK_NONE',
                    'SEXUAL': 'BLOCK_NONE',
                    'DANGEROUS': 'BLOCK_NONE'
                }
            )

            if hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
                print("Prompt was blocked due to the following reason:", response.prompt_feedback.block_reason)
                return "Unable to generate analysis due to content restrictions."

            if response.text:
                analysis_text = response.text
                with open(f"{output_folder}/response.json", 'w') as file:
                    json.dump(analysis_text, file)

                print(f"REDDIT AGENT: Completed analysis and saved the result to {output_folder}/response.json")
                self.task_completed = True
                return f"Analysis generated, and it is available at {output_folder}/response.json"
            else:
                print("No useful response was generated. Review the input or model configuration.")
                return "An error occurred during analysis."

        except Exception as e:
            self.task_completed = True
            print("An unexpected error occurred:", str(e))
            print("REDDIT AGENT: Task completed with error.")
            return "Failed to generate analysis due to an error."
        finally:
            # Ensures that task_completed is always set to True regardless of how the function exits
            self.task_completed = True
```
reddit_agent.py
```
import os
from dotenv import load_dotenv
import praw
import json
import google.generativeai as genai
from agents.agent_base import AgentBase

load_dotenv()
genai.configure(api_key=os.environ["API_KEY"])
client_id = os.getenv("REDDIT_CLIENT_ID")
client_secret = os.getenv("REDDIT_CLIENT_SECRET")
username = os.getenv("REDDIT_USERNAME")
password = os.getenv("REDDIT_PASSWORD")
reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    password=password,
    user_agent=f'script by /u/{username}',
    username=username
)
output_folder = "output/reddit_agent"
os.makedirs(output_folder, exist_ok=True)

class RedditAgent(AgentBase):
    def __init__(self):
        super().__init__()
        self.data_store = {}
        self.functions = {
            'retrieve_posts': self.retrieve_posts,
            'analyze_posts': self.analyze_posts,
            'retrieve_analysis': self.retrieve_analysis
        }
        self.model = genai.GenerativeModel(model_name='gemini-1.0-pro', tools=self.functions.values())
        self.chat = self.model.start_chat(enable_automatic_function_calling=True)
        
    def retrieve_posts(self, subreddits: list[str], mode: str = 'top', query: str = None, sort_by: str = 'relevance',
                       time_filter: str = 'all', limit: int = 100):
        """
            Retrieve posts from specified subreddits based on the given mode ('top' or 'search'). If mode is 'search',
            use the provided query and sort parameters. Store the results in a global data store.

            Args:
                subreddits (list[str]): List of subreddit names from which to retrieve posts.
                mode (str): Mode of operation ('top' or 'search'). Defaults to 'top'.
                query (str): Keyword query for searching posts. Required if mode is 'search'.
                sort_by (str): Sorting criterion ('relevance', 'hot', 'top', 'new', 'comments'). Applicable only for 'search'.
                time_filter (str): Time filter for posts ('hour', 'day', 'week', 'month', 'year', 'all'). Defaults to 'all'.
                limit (int): Maximum number of posts to retrieve.

            Returns:
                str: Result message indicating the number of posts and comments found and stored.
        """
        print(f"REDDIT AGENT: Retrieving posts.")
        total_comments = 0
        posts = []
        for sub in subreddits:
            subreddit = reddit.subreddit(sub)
            try:
                if mode == 'top':
                    found_posts = subreddit.top(time_filter=time_filter, limit=limit)
                elif mode == 'search':
                    found_posts = subreddit.search(query, sort=sort_by, time_filter=time_filter, limit=limit)
                else:
                    raise ValueError("Invalid mode specified. Use 'top' or 'search'.")

                for post in found_posts:
                    comments = self.retrieve_comments(post.id)
                    total_comments += len(comments)
                    print(f"\rTotal comments retrieved so far: {total_comments}", end='', flush=True)
                    post_details = {
                        'id': post.id,
                        'title': post.title,
                        'author': post.author.name if post.author else None,
                        'score': post.score,
                        'url': post.url,
                        'comments': comments,
                        'num_comments': post.num_comments
                    }
                    self.data_store[f'post_{post.id}'] = post_details
                    posts.append(post.id)
            except Exception as e:
                print(f"\nError accessing subreddit {sub}: {e}")

        print()
        self.data_store['post_ids'] = posts if posts else []

        result = f"Found {len(posts)} relevant posts with a total of {total_comments} comments retrieved."
        return result

    def retrieve_comments(self, post_id, sort='best', comment_limit=5):
        submission = reddit.submission(id=post_id)
        submission.comment_sort = sort
        submission.comments.replace_more(limit=0)
        comments = [(comment.body, comment.score) for comment in submission.comments.list()[:comment_limit]]
        return comments

    def analyze_posts(self, instruction: str):
        """
        Analyze posts after relevant posts have been found. You can summarize, perform sentiment analysis,
        or identify emerging topics.

        Args:
            instruction (str): Instructions for analysis, e.g., "Summarize these posts:", 
                            "Perform sentiment analysis for these posts:", or "Identify emerging topics for these posts:"

        Returns:
            str: Summary or analysis results, or a message indicating that no posts are available.
        """
        post_ids = self.data_store.get('post_ids', [])
        posts = [self.data_store[f'post_{post_id}'] for post_id in post_ids]

        if not posts:
            return "No posts data available for analysis."

        post_summaries = [f"Title: {post['title']}, Author: {post['author']}, Comments: {post['comments']}, Score: {post['score']}" 
                          for post in posts]
        summary_prompt = f"{instruction}\n\n{'; '.join(post_summaries)}"

        print("REDDIT AGENT: Analyzing posts...")
        response = self.pro_generate_analysis(summary_prompt, output_folder)
        return response
        # model = genai.GenerativeModel('gemini-1.5-pro-latest')
        # response = model.generate_content(summary_prompt)
        # print(response)
        
        # try:
        #     response = model.generate_content(
        #         summary_prompt,
        #         safety_settings={
        #             'HATE': 'BLOCK_NONE',
        #             'HARASSMENT': 'BLOCK_NONE',
        #             'SEXUAL': 'BLOCK_NONE',
        #             'DANGEROUS': 'BLOCK_NONE'
        #         }
        #     )

        #     if hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
        #         print("Prompt was blocked due to the following reason:", response.prompt_feedback.block_reason)
        #         return "Unable to generate analysis due to content restrictions."

        #     if response.text:
        #         analysis_text = response.text
        #         self.data_store['post_summary'] = analysis_text
        #         with open(f"{output_folder}/response.json", 'w') as file:
        #             json.dump(analysis_text, file)

        #         print(f"REDDIT AGENT: Completed analysis and saved the result to {output_folder}/response.json")
        #         self.task_completed = True
        #         return "Analysis generated."
        #     else:
        #         print("No useful response was generated. Review the input or model configuration.")
        #         return "An error occurred during analysis."

        # except Exception as e:
        #     self.task_completed = True
        #     print("An unexpected error occurred:", str(e))
        #     print("REDDIT AGENT: Task completed with error.")
        #     return "Failed to generate analysis due to an error."
        # finally:
        #     # Ensures that task_completed is always set to True regardless of how the function exits
        #     self.task_completed = True
    
    def retrieve_analysis(self):
        """Retrieve analysis generated earlier on.
        """
        print("Retrieving Analysis...")
        with open(f"{output_folder}/response.json", 'r') as file:
            # Read the file content
            json_text = file.read()
            
            # Parse the JSON data
            analysis = json.loads(json_text)

        print(f"Got the analysis:\n\n{analysis}")
        self.task_completed = True

        response = f"Analysis retrieved, here is the analysis:\n{analysis}"
        return response

    def generate_response(self, prompt):
        prompt = f"""
            Based on user input, search subreddits and analyze the result, limit posts to 10.

            User: {prompt}
        """
        result = self.execute_function_sequence(self.model, self.functions, prompt, self.chat)

        return "Done with analysis."
```
steam_agent.py
```
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
    def __init__(self):
        super().__init__()
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
        try:
            with open(reviews_file_path, 'r', encoding='utf-8') as file:
                reviews_data = json.load(file)
            reviews_details = reviews_data.get('reviews_details', [])
            if not reviews_details:
                return "No reviews data available for analysis."

            review_texts = [f"Review: {review['review']}" for review in reviews_details]
            analysis_prompt = f"{instruction}\n\n{' '.join(review_texts)}"

            response = self.pro_generate_analysis(analysis_prompt,output_folder)

            # model = genai.GenerativeModel('gemini-1.5-pro-latest')
            # response = model.generate_content(analysis_prompt)

            # with open(f"{output_folder}/response.json", 'w') as file:
            #     json.dump(response.text, file)
            # self.task_completed = True
            # return response.text
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
        result = self.execute_function_sequence(self.model, self.functions, prompt, self.chat)

        return "Done with review analysis."
```
agent_manager.py
```
import os
import importlib
from typing import List
from agents.agent_base import AgentBase
from dotenv import load_dotenv
import google.generativeai as genai
import json

load_dotenv()
genai.configure(api_key=os.environ["API_KEY"])
output_folder = "output/manager_agent"
os.makedirs(output_folder, exist_ok=True)

class AgentManager(AgentBase):
    def __init__(self):
        super().__init__()
        self.agents = []
        agent_modules = self.discover_agent_modules()
        for module_name in agent_modules:
            module = importlib.import_module(f"agents.{module_name}")
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, AgentBase) and attr != AgentBase:
                    self.agents.append(attr())
        self.data_store = {}
        self.delegated_agents = []
        # IMPORTANT: Function table must be defined for GEMINI API to call them!
        self.functions = {
            'delegate_to_steam_agent': self.delegate_to_steam_agent,
            'delegate_to_reddit_agent': self.delegate_to_reddit_agent,
            'summarize_agents_responses': self.summarize_agents_responses,
            'respond_to_user':self.respond_to_user,
            'chat_with_data':self.chat_with_data
        }
        # Initialize chat model with function call ability
        self.model = genai.GenerativeModel(model_name='gemini-1.0-pro', tools=self.functions.values())
        # Initialize basic data chat model, no functions
        self.data_chat_model = genai.GenerativeModel(model_name='gemini-1.0-pro')
        self.user_input = ""
        self.first_conversation = True
        self.chat = self.model.start_chat(enable_automatic_function_calling=True)

    def discover_agent_modules(self) -> List[str]:
        agent_modules = []
        agents_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "agents")
        for file in os.listdir(agents_dir):
            if file.endswith(".py") and file != "__init__.py" and file != "agent_base.py":
                agent_modules.append(file[:-3])
        return agent_modules

    def delegate_to_steam_agent(self, query: str):
        """
        Delegate the task to the steam agent.
        
        Args:
            query: instruction for steam agent to analyze a game. Must include a game's name.
        Returns:
            str: the status of the analysis.
        """
        print("MANAGER AGENT: DELEGATING TO STEAM AGENT")
        steam_agent = next((agent for agent in self.agents if agent.__class__.__name__.lower() == "steamagent"), None)
        if steam_agent:
            response = steam_agent.generate_response(query)
            self.data_store["steam_response"] = response
            self.delegated_agents.append("steam_agent")
            return f"Steam Agent: {response}"
        else:
            return "Steam agent not found."

    def delegate_to_reddit_agent(self, query: str):
        """
        Delegate the task to the reddit agent.
        
        Args:
            query: instruction for reddit agent to analyze a topic.
        Returns:
            str: the status of the analysis.
        """
        print("MANAGER AGENT: DELEGATING TO REDDIT AGENT")
        reddit_agent = next((agent for agent in self.agents if agent.__class__.__name__.lower() == "redditagent"), None)
        if reddit_agent:
            response = reddit_agent.generate_response(query)
            self.data_store["reddit_response"] = response
            self.delegated_agents.append("reddit_agent")
            return f"Reddit Agent: {response}"
        else:
            return "Reddit agent not found."
            

    def summarize_agents_responses(self):
        """
            Summarize all agents' responses AFTER they generated analysis.
            
            Args:
                instruction: instruction to write a detailed analysis, summarize and make a conclusion based on all agents' responses.
            Returns:
                str: the status of the agents' responses.
        """
        print("MANAGER AGENT: ATTEMPTING TO SUMMARIZE...")
        instruction = "You are the master agent that handles user input and delegates tasks to other agents. Now that all agents have completed their tasks, based on all agents' responses below, write a detailed analysis, summarize and make a conclusion as a response to back to the user."
        agent_responses = []
        for agent in self.delegated_agents:
            response_file_path = f"output/{agent}/response.json"
            if os.path.exists(response_file_path):
                with open(response_file_path, 'r') as file:
                    response_data = json.load(file)
                    agent_responses.append(response_data)

        if not agent_responses:
            return "No agent responses found for summarization."

        # if there's only 1 agent
        if len(agent_responses) == 1:
            print("MANAGER AGENT: Copying data from single agent...")
            agent_response =  agent_responses[0]
            with open(f"{output_folder}/response.json", 'w') as file:
                json.dump(agent_response, file)
            self.task_completed = True
            return f"Analysis generated by MANAGER AGENT, and it is available at {output_folder}/response.json"
        else:
            prompt = f"{instruction}\n\nUser Input: {self.user_input}\n\nAgent Responses:\n"
            for i, response in enumerate(agent_responses, start=1):
                prompt += f"Agent {i}: {response}\n"

            response = self.pro_generate_analysis(prompt, output_folder)
            # pro_model = genai.GenerativeModel('gemini-1.5-pro-latest')
            # print("MANAGER AGENT: Summarizing everything...")
            # print(f"MANAGER AGENT: Prompt for summary:\n\n{prompt}")
            # response = pro_model.generate_content(prompt)
            # with open(f"{output_folder}/response.json", 'w') as file:
            #     json.dump(response.text, file)
        

        return response
    def respond_to_user(self, message: str):
        """
        By default, if there are no suitable or available function, respond to the user directly based on user input.
        OR
        After retrieving analysis, share the analysis with the user.

        Args:
            message: your response to the user.
        Returns:
            str: Your response back to the user.
        """
        print(f"MANAGER AGENT: ATTEMMPTING TO RESPOND TO USER like this: {message}")
        self.task_completed = True
        return message
    
    def chat_with_data(self, message: str):
        """
        Generate response based on the data from response.json created earlier. This function can only be called after summarize_agents_responses has been called. User get to ask questions or chat with data.

        Args:
            message: user's chat input
        Returns:
            str: response back to the user.
        """
        agent_responses = []
        for agent in self.delegated_agents:
            response_file_path = f"output/{agent}/response.json"
            if os.path.exists(response_file_path):
                with open(response_file_path, 'r') as file:
                    response_data = json.load(file)
                    agent_responses.append(response_data)
        prompt = f"Context:\n{agent_responses}\n\nUser:\n{message}"
        response = self.data_chat_model.generate_content(prompt)

        return response.text
    
    def generate_response(self, user_prompt):
        # Reset task completed status whenever it is generating a response
        self.task_completed = False
        self.user_input = user_prompt

        if self.first_conversation:
            prompt = f"""You are an agent designed specifically to help users to do research on certain topics. Currently, you have access to reddit agents to research on subreddits, steam agent to research on game reviews, and a web search agent who can search the web and analyze webpages.
                
                Based on the user input, respond by using the respond_to_user function unless you decide to delegate your task to agents (steam or reddit). You can delegate to both or one of them or respond to the user directly.

                User: {user_prompt}
            """
            self.first_conversation = False
        else:
            prompt = f"{user_prompt}"
        response = self.execute_function_sequence(self.model, self.functions, prompt, self.chat)

        print("MANAGER: EXECUTED FUNCTIONS")


        return response

```