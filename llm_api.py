import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from colors import Colors

DEBUG_MODE = True

# Load the environment variables from the .env file
load_dotenv()

# Configure the API with your API key stored in an environment variable
genai.configure(api_key=os.environ["API_KEY"])

# Create a model instance
model = genai.GenerativeModel('gemini-1.0-pro-latest')

def call_google_llm_api(prompt):
    if DEBUG_MODE:
        # print(f"{Colors.GREEN}DEBUG: PROMPT SENT TO GEMINI API for master agent's prompt:\n\n{Colors.END}")
        print(f"{Colors.GREEN}{prompt}{Colors.END}")
        # print("\n\n END OF PROMPT")
    try:
        response = model.generate_content(prompt)
        # Convert the raw text response to JSON format
        json_response = json.dumps({"response": response.text})
        print(f"{Colors.BLUE}{json_response}{Colors.END}")
        return json_response
    except Exception as e:
        print(f"An error occurred: {e}")
        return None