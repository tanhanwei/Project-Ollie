import json
from agents.math_agent import MathAgent
from agents.language_agent import LanguageAgent
from llm_api import call_google_llm_api

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

agent_registry = {
    "Math Agent": math_agent,
    "Language Agent": language_agent
}

# Conversation loop
conversation_history = ""
user_input = input("User: ")

while True:
    # Update the conversation history and user input in the master agent's prompt
    prompt = master_agent_prompt.replace("<conversation_history>", conversation_history)
    prompt = prompt.replace("<user_input>", user_input)

    # Send the master agent prompt to the Google LLM API and get the response
    master_agent_response = call_google_llm_api(prompt)

    if master_agent_response is None:
        print("An error occurred while communicating with the LLM API.")
        break

    print("Master Agent Response:", master_agent_response)

    try:
        # Parse the JSON response
        response_dict = json.loads(master_agent_response)
        response_text = response_dict["response"]
        print("MASTER Response Text:", response_text)
        
        # Parse the response text as JSON
        delegations_dict = json.loads(response_text)
        delegations = delegations_dict["delegations"]
    except (json.JSONDecodeError, KeyError) as e:
        print("Error parsing response:", e)
        break

    # Execute the delegations
    for delegation in delegations:
        agent_name = delegation["agent"]
        task = delegation["task"]
        agent = agent_registry[agent_name]
        response = agent.generate_response(task)
        conversation_history += f"{agent_name}: {response}\n"

    # Check if all delegations have been completed
# Check if all delegations have been completed
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

Ensure that the JSON object is complete and properly formatted, with all required fields present and no extra text, formatting characters, or code blocks outside the JSON structure.

JSON Response:
"""

    master_agent_response = call_google_llm_api(prompt)

    # To check if it can respond correctly
    print(f"MASTER AGENT RESPONSE: {master_agent_response}")

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

    print(f"Convo History: {conversation_history}")

    # Check if the user wants to end the conversation
    if user_input.lower() in ["bye", "goodbye", "exit", "quit"]:
        break

    # Get the user's input for the next turn
    user_input = input("User: ")

# End the conversation
print("Master Agent: Thank you for the conversation. Have a great day!")