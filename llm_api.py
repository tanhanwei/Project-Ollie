import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

# Load the environment variables from the .env file
load_dotenv()

# Configure the API with your API key stored in an environment variable
genai.configure(api_key=os.environ["API_KEY"])

# Create a model instance
model = genai.GenerativeModel('gemini-1.0-pro-latest')

def call_google_llm_api(prompt):
    try:
        response = model.generate_content(prompt)
        # Convert the raw text response to JSON format
        json_response = json.dumps({"response": response.text})
        return json_response
    except Exception as e:
        print(f"An error occurred: {e}")
        return None