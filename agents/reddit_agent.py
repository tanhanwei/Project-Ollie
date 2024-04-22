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