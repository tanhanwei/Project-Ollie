import os
from dotenv import load_dotenv
import praw
import google.generativeai as genai
from google.protobuf.struct_pb2 import Struct
import google.ai.generativelanguage as glm

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

# Store the detailed data in a dictionary
data_store = {}

# def search_subreddits(topic: str, sort_by: str = 'relevance', limit: int = 10):
#     print("SEARCHING SUBREDDITS.\n")
#     subreddits = reddit.subreddits.search(query=topic, sort=sort_by, limit=limit)
#     data_store['subreddits'] = [sub.display_name for sub in subreddits]
#     return f"Found {len(data_store['subreddits'])} relevant subreddits."

def search_subreddits_and_retrieve_posts(subreddits: list[str], query: str, sort_by: str = 'relevance', time_filter: str = 'all', limit: int = 100):
        
    """
    Search target subreddits, retrieve posts from search results, and save to data_store.
    
    Args:
        subreddits: target subreddits, decide the list of relevant subreddits based on user input
        query: relevant keywords based on user input
        sort_by: can be "relevance", "hot", "top", "new", or "comments" 
    """
    
    # print(f"Querying subreddits: {subreddits} with query: {query}")
    posts = []
    for sub in subreddits:
        subreddit = reddit.subreddit(sub)
        try:
            found_posts = subreddit.search(query, sort=sort_by, time_filter=time_filter, limit=limit)
            for post in found_posts:
                # Fetch and store detailed post data immediately
                post_details = {
                    'id': post.id,
                    'title': post.title,
                    'author': post.author.name if post.author else None,
                    'score': post.score,
                    'url': post.url,
                    'num_comments': post.num_comments
                }
                # Store each post's details in a dictionary using post ID as key
                data_store[f'post_{post.id}'] = post_details
                posts.append(post)
            print(f"Posts found in {sub}: {len(posts)}")
        except Exception as e:
            print(f"Error searching in subreddit {sub}: {e}")
    data_store['post_ids'] = [post.id for post in posts]
    print(f"DATA STORE:\n\n {data_store}")
    return f"Found {len(data_store['post_ids'])} relevant posts."


def get_post_details(post_id: str):
    print("GETTING POST DETAILS.\n")
    post = reddit.submission(id=post_id)
    
    # DEBUG
    print(f"READING RAW POST DATA:\n\n {post}\n\n END OF RAW POST")
    data_store[f'post_{post_id}'] = {
        'title': post.title,
        'author': post.author.name if post.author else None,
        'score': post.score,
        'url': post.url,
        'num_comments': post.num_comments
    }
    return f"Retrieved details for post {post_id}."

def get_comments(post_id: str, sort_by: str = 'top', limit: int = 50):
    print("GETTING COMMENTS\n")
    post = reddit.submission(id=post_id)
    post.comment_sort = sort_by
    post.comments.replace_more(limit=0)
    data_store[f'comments_{post_id}'] = [comment.id for comment in post.comments.list()[:limit]]
    return f"Retrieved {len(data_store[f'comments_{post_id}'])} comments for post {post_id}."

def get_comment_details(comment_id: str):
    print("GETTING COMMENT DETAILS\n")
    comment = reddit.comment(id=comment_id)
    data_store[f'comment_{comment_id}'] = {
        'author': comment.author.name if comment.author else None,
        'body': comment.body,
        'score': comment.score
    }
    return f"Retrieved details for comment {comment_id}."

# def analyze_sentiment(text: str):
#     print("ANALYSING SENTIMENTS\n")
#     model = genai.GenerativeModel('gemini-1.0-pro-latest')
#     prompt = f"""
#     Please analyze the sentiment of the following text and provide a score between -1 (very negative) and 1 (very positive):
#     {text}
#     """
#     response = model.generate_content(prompt)
#     data_store['sentiment'] = response.text
#     return "Sentiment analysis completed."

def analyze_posts(instruction: str):
    """Analyze posts after relevant post have been found. You can summarize, perform sentiment analysis, or identiry emerging topics.

    Args:
        instruction: instructions for llm to analyze posts. Examples: "Summarize these posts:", "Perform sentiment analysis for these posts:", or "Identify emerging topics for these posts:"
    """
    print("ANALYSING POSTS\n")
    post_ids = data_store['post_ids']
    posts = [data_store[f'post_{post_id}'] for post_id in post_ids]
    # print(f"Analyzing these posts:\n\n {posts}")

    if not posts:
        return "No posts data available for summarization."

    post_summaries = [f"Title: {post['title']}, Author: {post['author']}, Score: {post['score']}" for post in posts]
    # comment_summaries = [f"Comments for {post_id}: {len(data_store[f'comments_{post_id}'])} comments." for post_id in post_ids]

    # Combine posts and comments into a single prompt for summarization
    summary_prompt = f"""
    {instruction}\n\n
    {'; '.join(post_summaries)}

    """

    # DEBUG
    print(f"SUMMARY PROMPT:\n\n {summary_prompt}")

    model = genai.GenerativeModel('gemini-1.0-pro-latest')
    response = model.generate_content(summary_prompt)
    data_store['post_summary'] = response.text
    return "Post summary generated."


def summarize_comments(comment_ids: list[str], num_sentences: int = 5):
    print("SUMMARIZING COMMENTS\n")
    comments = [data_store[f'comment_{comment_id}'] for comment_id in comment_ids if f'comment_{comment_id}' in data_store]
    if not comments:
        return "No comments data available for summarization."
    comment_summaries = [f"Author: {comment['author']}, Body: {comment['body']}, Score: {comment['score']}" for comment in comments]
    model = genai.GenerativeModel('gemini-1.0-pro-latest')
    prompt = f"""
    Please summarize the following Reddit comments in {num_sentences} sentences:
    {'; '.join(comment_summaries)}
    """
    response = model.generate_content(prompt)

    print(f"SUMMARY:\n\n")
    print(response)

    data_store['comment_summary'] = response.text
    return "Comment summary generated."

def set_task_as_done():
    """Call this function when you see 'Post summary generated.' to end your task."""
    done = True
    print("Set task triggered")
    return "Task Completed."

# Create a dictionary of functions
functions = {
    'search_subreddits_and_retrieve_posts': search_subreddits_and_retrieve_posts,
    'get_post_details': get_post_details,
    'get_comments': get_comments,
    'get_comment_details': get_comment_details,
    'analyze_posts': analyze_posts,
    'summarize_comments': summarize_comments,
    'set_task_as_done': set_task_as_done
}

# Initialize the Gemini model
model = genai.GenerativeModel(model_name='gemini-1.0-pro', tools=functions.values())

done = False

def execute_function_sequence(model, functions, prompt):
    print(f"Executing function with the following prompt:\n\n {prompt}")
    # Send initial prompt to model
    messages = [{'role': 'user', 'parts': [{'text': prompt}]}]
    while not done:
        print(f"Message History:\n\n {messages}")
        response = model.generate_content(messages)
        print(f"RESPONSE: \n\n {response}")
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'function_call'):
                # Assuming 'function_call' is a property that you can access directly
                function_call = part.function_call
                if function_call.args is None:
                    print("Function call has no arguments.")
                    continue
                result = call_function(function_call, functions)
                
                # Handling the function response with protobuf Struct
                s = Struct()
                s.update({'result': result})

                # Prepare the function response to be sent back to the model
                function_response = glm.Part(
                    function_response=glm.FunctionResponse(name=function_call.name, response=s))
                
                # Append the response to the message sequence
                messages.append({'role': 'model', 'parts': [part]})
                messages.append({'role': 'user', 'parts': [function_response]})
            else:
                # Return the text response if the part is not a function call
                return getattr(part, 'text', 'No text available')

def call_function(function_call, functions):
    function_name = function_call.name
    # Unpacking arguments correctly depending on their actual structure
    if function_call.args is None:
        print(f"No arguments passed to function {function_name}")
        return "Error: No arguments provided"
    function_args = {k: v for k, v in function_call.args.items()}
    return functions[function_name](**function_args)

# Example usage:
user_input = "What are the emerging topics about Singapore?"
prompt = f"""
    Based on user input, search subreddits and analyze the result, limit posts to 50.

    User: {user_input}
"""
result = execute_function_sequence(model, functions, prompt)

# # Retrieve the detailed data from the data store
# post_summary = data_store.get('post_summary')
# comment_summary = data_store.get('comment_summary')

# print("Post Summary:")
# print(post_summary)

# print("Comment Summary:")
# print(comment_summary)

print("Job done!")