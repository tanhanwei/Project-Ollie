import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.protobuf.struct_pb2 import Struct
import google.ai.generativelanguage as glm
import json

# Load the environment variables from the .env file
load_dotenv()

# Configure the API with your API key stored in an environment variable
genai.configure(api_key=os.environ["API_KEY"])

# Create the output folder if it doesn't exist
output_folder = "output"
os.makedirs(output_folder, exist_ok=True)

# Global data store dictionary
data_store = {}

# Create a dictionary of functions
functions = {}

# Initialize the Gemini model
model = genai.GenerativeModel(model_name='gemini-1.0-pro', tools=functions.values())
task_completed = False

def execute_function_sequence(model, functions, prompt):
    messages = [{'role': 'user', 'parts': [{'text': prompt}]}]
    while not task_completed:
        response = model.generate_content(messages)
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'function_call'):
                function_call = part.function_call
                if function_call.args is None:
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
        return "Error: No arguments provided"
    function_args = {k: v for k, v in function_call.args.items()}
    return functions[function_name](**function_args)

def generate_response(prompt):
    prompt = f"""
        Based on user input, perform the necessary actions and analyze the result.

        User: {prompt}
    """
    result = execute_function_sequence(model, functions, prompt)
    return data_store.get('summary', 'No summary available')

# Agent-specific code goes here
# ...

# Example usage:
# user_input = "..."
# response = generate_response(user_input)
# print(response) 