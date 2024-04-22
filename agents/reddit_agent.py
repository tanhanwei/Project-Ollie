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
            'analyze_posts': self.analyze_posts
        }
        self.model = genai.GenerativeModel(model_name='gemini-1.0-pro', tools=self.functions.values())
        
    def retrieve_posts(self, subreddits: list[str], mode: str = 'top', query: str = None, sort_by: str = 'relevance',
                       time_filter: str = 'all', limit: int = 100):
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
        post_ids = self.data_store.get('post_ids', [])
        posts = [self.data_store[f'post_{post_id}'] for post_id in post_ids]

        if not posts:
            return "No posts data available for analysis."

        post_summaries = [f"Title: {post['title']}, Author: {post['author']}, Comments: {post['comments']}, Score: {post['score']}" 
                          for post in posts]
        summary_prompt = f"{instruction}\n\n{'; '.join(post_summaries)}"

        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        response = model.generate_content(summary_prompt)
        
        self.data_store['post_summary'] = response.text

        with open(f"{output_folder}/response.json", 'w') as file:
            json.dump(response.text, file)

        self.task_completed = True
        return "Post summary generated."

    def generate_response(self, prompt):
        prompt = f"""
            Based on user input, search subreddits and analyze the result, limit posts to 10.

            User: {prompt}
        """
        result = self.execute_function_sequence(self.model, self.functions, prompt)

        return "Done with analysis."