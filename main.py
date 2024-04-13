import json
import re
from agents.math_agent import MathAgent
from agents.language_agent import LanguageAgent
from agents.market_analysis_agent import MarketAnalysisAgent
from llm_api import call_google_llm_api
from colors import Colors

# Load prompts from files
with open("prompts/master_agent_prompt.txt", "r") as file:
    master_agent_prompt = file.read()

with open("prompts/math_agent_prompt.txt", "r") as file:
    math_agent_prompt = file.read()

with open("prompts/language_agent_prompt.txt", "r") as file:
    language_agent_prompt = file.read()

# Predefined function table and agent instances
function_table = {
    "calculate": lambda expression: eval(expression),
    "translate": lambda text, target_lang: f"Translating '{text}' to {target_lang}"
}

math_agent = MathAgent("Math Agent", "Mathematics", function_table, math_agent_prompt)
language_agent = LanguageAgent("Language Agent", "Language", function_table, language_agent_prompt)
market_analysis_agent = MarketAnalysisAgent("Market Analysis Agent", "Market Analysis", function_table, "")

agent_registry = {
    "Math Agent": math_agent,
    "Language Agent": language_agent,
    "Market Analysis Agent": market_analysis_agent
}

def extract_provided_info(task_request, required_fields):
    prompt = f"""
    Given the following task request:
    "{task_request}"
    
    Extract the provided information and return a JSON object with the extracted details.
    The JSON object should have keys corresponding to the required information fields, and the values should be the extracted information if available, or an empty string if not provided.
    
    Required information fields:
    {", ".join(required_fields)}
    
    Example:
    Task request: "perform market research for open-world game in southeast asia, focus on demographics age between 18 and 25 years old."
    Required fields: industry, product_service_description, target_market_location, target_market_demographics
    Output:
    {{
        "industry": "video game",
        "product_service_description": "open-world game",
        "target_market_location": "southeast asia",
        "target_market_demographics": "age between 18 and 25 years old"
    }}

    JSON Output:
    """
    response = call_google_llm_api(prompt)
    try:
        provided_info = json.loads(response)
        return provided_info
    except (json.JSONDecodeError, KeyError):
        return {}

def collect_required_info(delegations, user_input):
    required_info = {}
    required_fields = []

    for delegation in delegations:
        agent_name = delegation["agent"]
        agent = agent_registry.get(agent_name)
        if agent:
            agent_required_fields = agent.get_required_info()
            for field in agent_required_fields:
                if field not in required_fields:
                    required_fields.append(field)

    provided_info_response = extract_provided_info(user_input, required_fields)
    provided_info_json = provided_info_response["response"]

    # Use regular expressions to extract the JSON data from the response
    json_match = re.search(r'```\s*(?:JSON|json)\s*(.*?)\s*```', provided_info_json, re.DOTALL)
    if json_match:
        json_data = json_match.group(1)
        # Remove any escape characters and parse the JSON
        json_data = json_data.replace("\\", "")
        provided_info = json.loads(json_data)
        required_info.update(provided_info)

    missing_fields = [field for field in required_fields if required_info.get(field) is None or (isinstance(required_info.get(field), str) and required_info.get(field).strip() == "")]

    if missing_fields:
        print("Please provide the following additional information:")
        for field in missing_fields:
            user_input = input(f"{field}: ")
            required_info[field] = user_input

    return required_info

# Conversation loop
conversation_history = ""
user_input = input("User: ")

while True:
    # Update the conversation history and user input in the master agent's prompt
    prompt = master_agent_prompt.replace("<conversation_history>", conversation_history)
    prompt = prompt.replace("<user_input>", user_input)

    # DEBUG
    print("PROMPT FOR MASTER AGENT:\n\n")

    master_agent_response = call_google_llm_api(prompt)

    if master_agent_response is None:
        print("An error occurred while communicating with the LLM API.")
        break

    # Parse the JSON response
    response_dict = json.loads(master_agent_response)
    response_text = response_dict["response"]
    delegations_dict = json.loads(response_text)
    delegations = delegations_dict["delegations"]

    # Collect and validate the required information for all delegations
    required_info = collect_required_info(delegations, user_input)

    # Process each delegation
    for delegation in delegations:
        agent_name = delegation["agent"]
        task_type = delegation["task"]
        
        # Get the relevant agent
        agent = agent_registry.get(agent_name)
        
        if agent:
            # Filter the required information for the current agent
            agent_required_info = {field: value for field, value in required_info.items() if field in agent.get_required_info()}
            
            # Pass the required information to the agent
            response = agent.generate_response(agent_required_info)
            conversation_history += f"{agent_name}: {response}\n"
        else:
            print()
            conversation_history += f"No agent found for task type: {task_type}\n"

    # Check if all delegations have been completed
    prompt = f"""
Given the following conversation history:

{conversation_history}

Determine if all the delegated tasks have been completed and provide a final response to the user. If the tasks are not yet completed, indicate what additional information or tasks are needed.

Please respond with a well-formatted JSON object using the following structure:
{{
  "tasks_completed": true or false,
  "final_response": "Final response to the user if tasks are completed",
  "additional_info_needed": "Additional information or tasks needed if not completed"
}}

Ensure that the JSON object is complete and properly formatted, without any extra text, formatting characters, or code blocks.

JSON Response:
"""

    master_agent_response = call_google_llm_api(prompt)

    if master_agent_response is None:
        print("An error occurred while communicating with the LLM API.")
        break

    try:
        # Parse the JSON response
        response_dict = json.loads(master_agent_response)
        response_text = response_dict["response"]
        
        # Remove any extra text, formatting characters, or code blocks
        response_text = response_text.strip()
        response_text = response_text.replace("\`\`\`json", "").replace("\`\`\`", "")
        response_text = response_text.strip()

        if response_text.startswith("{") and response_text.endswith("}"):
            result_dict = json.loads(response_text)
            tasks_completed = result_dict.get("tasks_completed", False)
            final_response = result_dict.get("final_response", "")
            additional_info_needed = result_dict.get("additional_info_needed", "")
        else:
            raise json.JSONDecodeError("Invalid JSON format", response_text, 0)

        if tasks_completed:
            conversation_history += f"Master Agent: {final_response}\n"
            print(final_response)
        else:
            conversation_history += f"Master Agent: {additional_info_needed}\n"
            print(additional_info_needed)
    except (json.JSONDecodeError, KeyError) as e:
        print("Error parsing response:", e)
        conversation_history += "Master Agent: I apologize, but I couldn't generate a proper response. Can you please try rephrasing your request?\n"
        print("I apologize, but I couldn't generate a proper response. Can you please try rephrasing your request?")

    # Check if the user wants to end the conversation
    if user_input.lower() in ["bye", "goodbye", "exit", "quit"]:
        break

    # Get the user's input for the next turn
    user_input = input("User: ")

# End the conversation
print("Master Agent: Thank you for the conversation. Have a great day!")