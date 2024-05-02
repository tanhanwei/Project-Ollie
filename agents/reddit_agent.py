import os
from dotenv import load_dotenv
import praw
import json
import google.generativeai as genai
from agents.agent_base import AgentBase
from utils.file import File
from app_constants import RESPONSE, RESPONSE_STYLE

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
output_folder = f"output/{__name__.split('.')[-1]}"
response_path = f"{output_folder}/{RESPONSE}"

class RedditAgent(AgentBase):
    description = "An agent that can retrieve reddit posts and analyse them. It can be used to research any topics including games, technology, science, etc"
    def __init__(self):
        self.functions = self.get_functions() 
        super().__init__()
        self.data_store = {}
        os.makedirs(output_folder, exist_ok=True)

    def get_functions(self):
        return {
        # 'retrieve_posts': self.retrieve_posts,
        # 'analyze_posts': self.analyze_posts,
        # 'retrieve_analysis': self.retrieve_analysis,
        'retrieve_and_analyze_posts':self.retrieve_and_analyze_posts
        }
    
    def retrieve_posts(self, subreddits: list[str], mode: str = 'top', query: str = None, sort_by: str = 'relevance',
                       time_filter: str = 'all', limit: int = 100):
        """
            Retrieve posts from specified subreddits based on the given mode ('top' or 'search'). If mode is 'search',
            use the provided query and sort parameters. Store the results in a global data store.

            Args:
                subreddits (list[str]): List of subreddit names from which to retrieve posts.
                mode (str): Mode of operation ('top' or 'search'). Defaults to 'top'.
                query (str): Keyword query for searching posts. Required if mode is 'search'. DO NOT use full sentence. Use keyword(s) only.
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

                self.emit_debug_message(f"**REDDIT AGENT:** Retrieving comments...", "REDDIT AGENT")
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
        # summary_prompt = f"{instruction}\n\n{'; '.join(post_summaries)}"

        summary_prompt = f"""
        {instruction}

        {RESPONSE_STYLE}

        Here are the posts:

        {post_summaries}
        """        

        print("REDDIT AGENT: Analyzing posts...")
        self.emit_debug_message(f"**REDDIT AGENT:** Analyzing posts...", "REDDIT AGENT")
        analysis = self.pro_generate_analysis(summary_prompt)

        File.write_md(analysis,response_path)
        return f"Review analysis has been completed and is saved in '{output_folder}'"

    
    def retrieve_analysis(self):
        """Retrieve analysis generated earlier on.
        """
        print("Retrieving Analysis...")
        analysis = File.read_md(response_path)

        print(f"Got the analysis:\n\n{analysis}")

        response = f"Analysis retrieved, here is the analysis:\n{analysis}"
        return response
    
    def retrieve_and_analyze_posts(self, subreddits: list[str], mode: str = 'top', query: str = None, sort_by: str = 'relevance', time_filter: str = 'all', limit: int = 100, instruction: str = 'Analyze these posts'):
        """
            Retrieve posts from specified subreddits based on the given mode ('top' or 'search'). If mode is 'search',
            use the provided query and sort parameters. Store the results in a global data store. And finally analyze everything.

            Args:
                subreddits (list[str]): List of subreddit names (no spaces allowed) from which to retrieve posts. NOTE: NO SPACES or special characters for subreddit names.
                mode (str): Mode of operation ('top' or 'search'). Defaults to 'top'.
                query (str): Keyword query for searching posts. Required if mode is 'search'. DO NOT use full sentence. Use keyword(s) only.
                sort_by (str): Sorting criterion ('relevance', 'hot', 'top', 'new', 'comments'). Applicable only for 'search'.
                time_filter (str): Time filter for posts ('hour', 'day', 'week', 'month', 'year', 'all'). Defaults to 'all'.
                limit (int): Maximum number of posts to retrieve.
                instruction (str): Instructions for analysis, e.g., "Summarize these posts:", "Perform sentiment analysis for these posts:", or "Identify emerging topics for these posts:"

            Returns:
                str: Result message indicating the number of posts and comments found and stored.
        """

        subreddits = File.remove_spaces(subreddits)

        # To show the subreddit text
        subreddit = ""
        if len(subreddits) == 1:
            subreddit = subreddits[0]
        elif len(subreddits) > 1:
            for sub in subreddits:
                subreddit = f"{subreddit}, {sub}"
        else:
            subreddit = 'no subreddit'


        self.emit_debug_message(f"**REDDIT AGENT:** Ok, checking out {mode} posts on {subreddit} subreddit", "REDDIT AGENT")       
        status = self.retrieve_posts(subreddits, mode, query, sort_by, time_filter, limit)
        self.emit_debug_message(f"**REDDIT AGENT:** {status}", "REDDIT AGENT")
        status = self.analyze_posts(instruction)
        self.emit_debug_message(f"**REDDIT AGENT:** {status}", "REDDIT AGENT")


    def generate_response(self, prompt):
        prompt = f"""
            Based on user input, search subreddits and analyze the result, limit posts to 10.

            User: {prompt}
        """
        response = self.execute_function_sequence(self.model, self.functions, prompt, self.chat)

        return response