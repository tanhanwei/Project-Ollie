import os
from dotenv import load_dotenv
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import urllib.parse

# Load the environment variables from the .env file
load_dotenv()

# Configure the API with your API key stored in an environment variable
genai.configure(api_key=os.environ["API_KEY"])

# Create a model instance
model = genai.GenerativeModel('gemini-1.0-pro-latest')

def perform_search(query):
    try:
        # Encode the search query
        encoded_query = urllib.parse.quote(query)
        
        url = f'https://www.google.com/search?q={encoded_query}'
        print(f"Search URL: {url}")
        
        response = requests.get(url)
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Content:\n{response.text}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        print(f"Parsed HTML:\n{soup.prettify()}")
        
        # Extract relevant information from the search results
        search_results = []
        # Extract relevant information from the search results
        search_results = []
        for result in soup.find_all('div', class_='g'):
            link_element = result.find('a')
            if link_element:
                link = link_element['href']
                title = getattr(link_element, 'text', '')
                description = getattr(result.find('div', class_='s'), 'text', '')
                search_results.append({'title': title, 'link': link, 'description': description})
        
        return search_results
    except Exception as e:
        print(f"An error occurred during the search: {e}")
        return []

def read_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract the main content from the page
    main_content = soup.select_one('body').get_text(strip=True)
    
    return main_content

def generate_response(user_input, search_results=None):
    if search_results:
        # Log the search results
        print("Search Results:")
        for index, result in enumerate(search_results, start=1):
            print(f"{index}. Title: {result['title']}")
            print(f"   Link: {result['link']}")
            print(f"   Description: {result['description']}")
            print()
        
        # Access and read the content of each top result
        summaries = []
        for result in search_results:
            url = result['link']
            content = read_url(url)
            
            # Log the content read by the model
            print(f"Content from {url}:")
            print(content)
            print()
            
            # Summarize the content using the model
            summary = model.generate_content(f"Please summarize the following text: {content}")
            summaries.append(summary.text)
        
        # Generate a response based on the summaries
        response_text = f"Here are the summaries of the top search results for '{user_input}':\n\n" + "\n".join(summaries)
    else:
        # Generate a generic response
        response_text = f"Hello, who are you? Can you tell me about your origin? {user_input}"
    
    try:
        response = model.generate_content(response_text)
        return response.text
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# First user input
user_input = input("You: ")

# Perform the search based on the user's input
search_query = user_input
search_results = perform_search(search_query)

# Select the top 3 search results
top_results = search_results[:3]

print(f"TOP RESULT:\n{top_results}")

while True:
    # Generate a response from the model
    response = generate_response(user_input, top_results)
    if response:
        print("Gemini:", response)
    
    # Input your message
    user_input = input("You: ")
    
    # Check if the user wants to exit the chat
    if user_input.lower() in ['exit', 'quit']:
        print("Exiting chat. Goodbye!")
        break
    
    # Perform a new search based on the user's input
    search_query = user_input
    search_results = perform_search(search_query)
    top_results = search_results[:3]