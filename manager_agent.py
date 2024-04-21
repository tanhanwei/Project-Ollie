import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.protobuf.struct_pb2 import Struct
import google.ai.generativelanguage as glm
import json
from steam_agent import generate_response as steam_generate_response
from reddit_agent import generate_response as reddit_generate_response
from colors import print_blue, print_green, print_red, print_yellow

# Load the environment variables from the .env file
load_dotenv()

# Configure the API with your API key stored in an environment variable
genai.configure(api_key=os.environ["API_KEY"])

# Create the output folder if it doesn't exist
output_folder = "output/manager_agent"
os.makedirs(output_folder, exist_ok=True)

# Global data store dictionary
data_store = {}
delegated_agents = []

def delegate_to_steam_agent(query: str):
    """
    Delegate the task to the steam agent.
    
    Args:
        query: instruction for steam agent to analyze a game. Must include a game's name.
    Returns:
        str: the status of the analysis.
    """
    print_red("DELEGATING TO STEAM AGENT")
    response = steam_generate_response(query)
    data_store['steam_response'] = response
    delegated_agents.append('steam_agent')
    return f"Steam Agent: {response}"

def delegate_to_reddit_agent(query: str):
    """
    Delegate the task to the reddit agent.
    
    Args:
        query: instruction for reddit agent to analyze a topic.
    Returns:
        str: the status of the analysis.
    """
    print_red("DELEGATING TO REDDIT AGENT")
    response = reddit_generate_response(query)
    data_store['reddit_response'] = response
    delegated_agents.append('reddit_agent')
    return f"Reddit Agent: {response}"

def summarize_agents_responses():
    """
    Summarize all agents' responses.
    
    Args:
        instruction: instruction to write a detailed analysis, summarize and make a conclusion based on all agents' responses.
    Returns:
        str: the status of the agents' responses.
    """
    print_red("DELEGATING TO SUMMARY AGENT")
    instruction = "You are the master agent that handles user input and delegates tasks to other agents. Now that all agents have completed their tasks, based on all agents' responses below, write a detailed analysis, summarize and make a conclusion as a response to back to the user."
    agent_responses = []
    for agent in delegated_agents:
        response_file_path = f"output/{agent}/response.json"
        print_red(f"READING AGENTS RESPONSE FILE FROM: {response_file_path}")
        if os.path.exists(response_file_path):
            print_red("FILE EXIST!")
            with open(response_file_path, 'r') as file:
                response_data = json.load(file)
                agent_responses.append(response_data)
        else:
            print_red("FILE DOES NOT EXIST!")

    if not agent_responses:
        return "No agent responses found for summarization."

    prompt = f"{instruction}\n\nUser Input: {user_input}\n\nAgent Responses:\n"
    for i, response in enumerate(agent_responses, start=1):
        prompt += f"Agent {i}: {response}\n"
    print_red("ANALYZING...")
    pro_model = genai.GenerativeModel('gemini-1.5-pro-latest')
    response = pro_model.generate_content(prompt)
    # Save the post summary to a JSON file
    with open(f"{output_folder}/response.json", 'w') as file:
        json.dump(response.text, file)
    print_red(f"ANALYSIS COMPLETED and response saved to {output_folder}")
    global task_completed
    task_completed = True

    return "Analysis completed by master agent."

# Create a dictionary of functions
functions = {
    'delegate_to_steam_agent': delegate_to_steam_agent,
    'delegate_to_reddit_agent': delegate_to_reddit_agent,
    'summarize_agents_responses': summarize_agents_responses
}

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
        Based on the user input, determine which agent (steam or reddit) should handle the task and delegate accordingly. You can delegate to both or one of them. Your task ends when you decide to summarize everything that you have so far.

        User: {prompt}
    """
    result = execute_function_sequence(model, functions, prompt)

    print_red(f"STATUS: {result}")
    
    # # Save the manager's response to a JSON file
    # with open(f"{output_folder}/manager_response.json", 'w') as file:
    #     json.dump(result, file)

    return result

# Example usage:
user_input = "Tell me about the latest discussions on the game called Vampire Survivors."
response = generate_response(user_input)
print(response)