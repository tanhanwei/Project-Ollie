import os
import json
from dotenv import load_dotenv  # Import the load_dotenv function
import google.generativeai as genai

# Load the environment variables from the .env file
load_dotenv()

# Configure the API with your API key stored in an environment variable
genai.configure(api_key=os.environ["API_KEY"])

# Create a model instance
model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])

def ask_user(question):
    """Function to ask the user a question and get their input."""
    print(question)  # Print the question to the console
    return input("Your response: ")  # Wait for and return the user's input

def process_response(prompt):
    """Function to send the prompt to the model and process its response."""
    response = model.generate_content(prompt)
    # response = chat.send_message(prompt)
    # DEBUG: Print repsonse
    print(f"RESPONSE:\n\n{response.text}")
    try:
        response_data = json.loads(response.text)  # Try to parse the response as JSON
        action = response_data["decision"]["action"]
        param = response_data["decision"]["param"]
        latest_summary = response_data["latest_summary"]
        return latest_summary,action, param
    except json.JSONDecodeError:
        print("Failed to decode response as JSON.")
        return None, None

# Setup

area = "business idea evaluation"
agent_function = "evaluate if it is a good idea"

previous_output = "What kind of business do you want to start?"
user_input = "I want to start a business"

latest_summary = "Nothing, this is the beginning of a conversation"




# response = model.generate_content(prompt)
# print(response.text)

# Interaction Loop
while True:
    
    prompt = f"""
    # System  
    
    You are an agent that specialise in {area}, and you are one of the agents in a multi-agent system. Your first task is to understand what the user wants before creating a plan for yourself to {agent_function}.

    # Your previous output
    {previous_output}
    
    # User Input
    {user_input}

    # Summary of User Intent
    {latest_summary}
    
    # Task  
    
    Based on "Your previous output", "User Input", and "Summary of User Intent", did the user answer your question?
    Do you have enough information before writing an action plan?  Please ensure that you have all relevant information from the user before proceeding.
    
    If the user's intention and plan is NOT clear, ask the user by responding with the following json structure without repeating the same question:  
    
    {{  
        "decision": {{
            "action": "ask",
            "param": "<follow-up question for the user>"
        }},
        "latest_summary": "<summarize the user's intention, DO NOT use the word "you", use "user" instead.>"
    }}

    If the user is not sure by saying "I don't know","not sure", "no idea", or asking you to suggest and recommend,
    DO NOT repeat the same question as your previous output!
    Instead, you can give your suggestion and ask for confirmation:

        {{  
        "decision": {{
            "action": "suggest",
            "param": "<suggestions for the user, ask if ok>"
        }},
        "latest_summary": "<summarize the conversation and include the user's latest input>"
    }}

    If the user's intention and plan is VERY clear, summarize the user’s input and intention and respond with the following json structure (DO NOT choose the "next" action if there are ANY ambiguities):  
    
    {{  
        "decision": {{
            "action": "next",
            "param": "<summary of user input and intention>"
        }},
        "latest_summary": "<latest summary of user input and intention>"
    }}  
    """
    print(f"PROMPT:\n\n{prompt}")
    latest_summary,action, param = process_response(prompt)
    if action == "ask" or action == "suggest":
        previous_output = param
        user_input = ask_user(param)  # Get follow-up input from the user
        # latest_summary += f" {param} {user_input}"  # Update the latest summary with the interaction
    elif action == "next":
        print("AI decision:", param)
        break  # Exit the loop if the action is to proceed to the next step    