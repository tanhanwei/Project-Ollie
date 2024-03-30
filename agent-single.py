import os
from dotenv import load_dotenv  # Import the load_dotenv function
import google.generativeai as genai

# Load the environment variables from the .env file
load_dotenv()

# Configure the API with your API key stored in an environment variable
genai.configure(api_key=os.environ["API_KEY"])

# Create a model instance
model = genai.GenerativeModel('gemini-1.0-pro-latest')

# Setup

area = "business idea evaluation"
agent_function = "evaluate if it is a good idea"

user_input = "I want to sell chicken rice"

latest_summary = "Nothing, this is the beginning of a conversation"

prompt = f"""
# System  
  
You are an agent that specialise in {area}, and you are one of the agents in a multi-agent system. Your first task is to understand what the user wants before creating a plan for yourself to {agent_function}.

# User Input
{user_input}

# Latest Summary
{latest_summary}
  
# Task  
  
Do you have enough information before writing an action plan?  
  
If yes, summarize the user’s input and intention and respond with the following json structure:  
  
{{  
	"decision": {{
		"action": "next",
		"param": "<summary of user input and intention>"
	}},
	"latest_summary": "<latest summary of user input and intention>"
}}  
  
If no, respond with the following json structure:  
  
{{  
	"decision": {{
		"action": "ask",
		"param": "<follow-up question for the user>"
	}},
	"latest_summary": "<latest summary of your decision, user input and intention>"
}}  
"""

response = model.generate_content(prompt)
print(response.text)