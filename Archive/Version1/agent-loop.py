import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load the environment variables from the .env file
load_dotenv()

# Configure the API with your API key stored in an environment variable
genai.configure(api_key=os.environ["API_KEY"])

# Create a model instance
model = genai.GenerativeModel('gemini-1.0-pro-latest')

while True:
    # Input your message
    user_input = input("You: ")
    # Check if the user wants to exit the chat
    if user_input.lower() in ['exit', 'quit']:
        print("Exiting chat. Goodbye!")
        break

    # Generate a response from the model
    try:
        response = model.generate_content(f"{user_input}")
        print("Gemini:", response.text)
    except Exception as e:
        print(f"An error occurred: {e}")
        break
