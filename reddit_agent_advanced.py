import os
from dotenv import load_dotenv
import praw
import google.generativeai as genai
from google.protobuf.struct_pb2 import Struct
import google.ai.generativelanguage as glm
from colors import print_blue, print_green, print_red, print_yellow
import sys

# Load the environment variables from the .env file
load_dotenv()

# Configure the API with your API key stored in an environment variable
genai.configure(api_key=os.environ["API_KEY"])

# Accessing variables from environment
client_id = os.getenv("REDDIT_CLIENT_ID")
client_secret = os.getenv("REDDIT_CLIENT_SECRET")
username = os.getenv("REDDIT_USERNAME")
password = os.getenv("REDDIT_PASSWORD")

# Setup PRAW
reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    password=password,
    user_agent=f'script by /u/{username}',
    username=username
)

# Global data store dictionary
data_store = {}

def retrieve_posts(subreddits: list[str], mode: str = 'top', query: str = None, sort_by: str = 'relevance',
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
    print_red(f"Accessing {subreddits} with mode: {mode}, query: {query}, sorting by: {sort_by} with limit: {limit}")
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
                comments = retrieve_comments(post.id)
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
                data_store[f'post_{post.id}'] = post_details
                posts.append(post.id)
        except Exception as e:
            print(f"\nError accessing subreddit {sub}: {e}")

    print()
    data_store['post_ids'] = posts if posts else []

    print_green(f"\nDATA STORE:\n {data_store}")
    result = f"Found {len(posts)} relevant posts with a total of {total_comments} comments retrieved."
    return result

def retrieve_comments(post_id, sort='best', comment_limit=5):
    """Retrieve top-level comments from a specific post sorted by a given method."""
    submission = reddit.submission(id=post_id)
    submission.comment_sort = sort
    submission.comments.replace_more(limit=0)
    comments = [(comment.body, comment.score) for comment in submission.comments.list()[:comment_limit]]
    return comments

def analyze_posts(instruction: str):
    """
    Analyze posts after relevant posts have been found. You can summarize, perform sentiment analysis,
    or identify emerging topics.

    Args:
        instruction (str): Instructions for analysis, e.g., "Summarize these posts:", 
                           "Perform sentiment analysis for these posts:", or "Identify emerging topics for these posts:"

    Returns:
        str: Summary or analysis results, or a message indicating that no posts are available.
    """
    print_red("Analysing posts...")
    post_ids = data_store.get('post_ids', [])
    posts = [data_store[f'post_{post_id}'] for post_id in post_ids]

    if not posts:
        return "No posts data available for analysis."

    post_summaries = [f"Title: {post['title']}, Author: {post['author']}, Comments: {post['comments']}, Score: {post['score']}" 
                      for post in posts]
    summary_prompt = f"{instruction}\n\n{'; '.join(post_summaries)}"

    print_green(f"SUMMARY PROMPT:\n\n {summary_prompt}")

    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    response = model.generate_content(summary_prompt)
    print_red(f"RESPONSE DEBUG:\n {response}")

    data_store['post_summary'] = response.text
    global task_completed
    task_completed = True
    return "Post summary generated."

def set_task_as_done():
    """Call this function when you see 'Post summary generated.' to end your task."""
    global task_completed
    task_completed = True
    print("Set task triggered")
    return "Task Completed."

# Create a dictionary of functions
functions = {
    'retrieve_posts': retrieve_posts,
    'analyze_posts': analyze_posts,
    'set_task_as_done': set_task_as_done
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

# Example usage:
user_input = "Find out about emerging topic in the latest singularity subreddit."
prompt = f"""
    Based on user input, search subreddits and analyze the result, limit posts to 10.

    User: {user_input}
"""
result = execute_function_sequence(model, functions, prompt)

# TODO: Maybe can save the result (summary) elsewhere so that the agent manager can access later. All it needs to know is that post summary has been generated.

print(result)
print(data_store['post_summary'])

print("Job done!")