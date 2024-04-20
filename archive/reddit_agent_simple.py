import os
from dotenv import load_dotenv
import praw
import google.generativeai as genai
from llm_api import call_google_llm_api

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

def subreddit_search_with_comments(subreddit_name, sort='best', limit=3):
    """ Search for the latest top posts from a specific subreddit and retrieve comments for each post. """
    subreddit = reddit.subreddit(subreddit_name)
    top_posts = subreddit.top(time_filter='day', limit=limit)
    posts_comments = []

    for post in top_posts:
        comments = retrieve_comments(post.id, sort)
        post_info = {
            'title': post.title,
            'url': post.url,
            'id': post.id,
            'comments': comments
        }
        posts_comments.append(post_info)

    return posts_comments

def retrieve_comments(post_id, sort='best', comment_limit=10):
    """ Retrieve top-level comments from a specific post sorted by a given method. """
    submission = reddit.submission(id=post_id)
    submission.comment_sort = sort
    submission.comments.replace_more(limit=0)
    comments = [(comment.body, comment.score) for comment in submission.comments.list()[:comment_limit]]
    return comments

def print_posts_with_comments(posts_comments):
    """ Print posts and their comments in a formatted manner. """
    for post in posts_comments:
        print(f"\nPost Title: {post['title']}")
        print(f"URL: {post['url']}")
        print(f"Post ID: {post['id']}")
        print("Comments:")
        for comment, score in post['comments']:
            print(f" - {comment} [Score: {score}]")

def summarize(posts_comments):
    print(posts_comments)
    # Create a model instance
    model = genai.GenerativeModel('gemini-1.0-pro-latest')

    # Format the posts and their comments into a readable string
    formatted_posts = []
    for post in posts_comments:
        comments = '; '.join([f"{comment[0]} [Score: {comment[1]}]" for comment in post['comments']])
        formatted_post = f"Title: {post['title']}, Comments: {comments}"
        formatted_posts.append(formatted_post)
    
    prompt = f"""
        Please summarize the following Reddit posts and comments:
        {'; '.join(formatted_posts)}
    """
    response = model.generate_content(prompt)
    return response.text



def search_and_summarize(subreddit_name: str):
    """
    Summarize retrieved comments for subreddit posts based on the specified subreddit name.

    Args:
        subreddit_name: Subreddit name
    """
    subreddit_posts_comments = subreddit_search_with_comments(subreddit_name, 'best', 5)
    summary = summarize(subreddit_posts_comments)
    return summary

functions = {
    'search_and_summarize': search_and_summarize,
}

def call_function(function_call, functions):
    function_name = function_call.name
    function_args = function_call.args
    return functions[function_name](**function_args)

model = genai.GenerativeModel(model_name='gemini-1.0-pro',
                              tools=functions.values())
# Example usage:
# subreddit_posts_comments = subreddit_search_with_comments("Python", 'best', 2)
# print_posts_with_comments(subreddit_posts_comments)

print("Reddit Agent: Hello, what would you like to find out from Reddit?")
user_input = input("You: ")

response = model.generate_content(user_input)

part = response.candidates[0].content.parts[0]

if part.function_call:
    result = call_function(part.function_call, functions)

print(result)

# print(response)