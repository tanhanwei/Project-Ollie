import json
import re
from .agent import Agent
from llm_api import call_google_llm_api


class ManagerAgent(Agent):
    def __init__(self, name, expertise, function_table, prompt, managed_agents):
        super().__init__(name, expertise, function_table, prompt)
        self.managed_agents = {agent.name: agent for agent in managed_agents}

    def extract_provided_info(self, task_request, required_fields):
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

    def collect_required_info(self, delegations, input_data):
        required_info = {}
        required_fields = []

        for delegation in delegations:
            agent_name = delegation["agent"]
            agent = self.managed_agents.get(agent_name)
            if agent:
                agent_required_fields = agent.get_required_info()
                for field in agent_required_fields:
                    if field not in required_fields:
                        required_fields.append(field)

        provided_info_response = self.extract_provided_info(input_data, required_fields)
        provided_info_json = provided_info_response["response"]

        json_match = re.search(r'```\s*(?:JSON|json)\s*(.*?)\s*```', provided_info_json, re.DOTALL)
        if json_match:
            json_data = json_match.group(1)
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

    def delegate_tasks(self, input_data):
        if isinstance(input_data, dict):
            input_data = json.dumps(input_data)

        prompt = self.prompt.replace("<conversation_history>", "")
        prompt = prompt.replace("<user_input>", input_data)
        response = call_google_llm_api(prompt)

        if response is None:
            print("An error occurred while communicating with the LLM API.")
            return []

        try:
            response_dict = json.loads(response)
            response_text = response_dict["response"]
            delegations_dict = json.loads(response_text)
            delegations = delegations_dict["delegations"]
        except (json.JSONDecodeError, KeyError):
            print("Error parsing response from the LLM API.")
            return []

        return delegations

    def process_delegations(self, delegations, required_info):
        conversation_history = ""
        for delegation in delegations:
            agent_name = delegation["agent"]
            agent = self.managed_agents.get(agent_name)
            if agent:
                agent_required_info = {field: value for field, value in required_info.items() if field in agent.get_required_info()}
                if isinstance(agent, ManagerAgent):
                    response = agent.run(agent_required_info)
                else:
                    response = agent.generate_response(agent_required_info)
                conversation_history += f"{agent_name}: {response}\n"
            else:
                conversation_history += f"No agent found for task: {delegation['task']}\n"
        return conversation_history

    def check_task_completion(self, conversation_history):
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
        response = call_google_llm_api(prompt)
        try:
            response_dict = json.loads(response)
            response_text = response_dict["response"]
            response_text = response_text.strip()
            response_text = response_text.replace("\`\`\`json", "").replace("\`\`\`", "")
            response_text = response_text.strip()
            if response_text.startswith("{") and response_text.endswith("}"):
                result_dict = json.loads(response_text)
                tasks_completed = result_dict.get("tasks_completed", False)
                final_response = result_dict.get("final_response", "")
                additional_info_needed = result_dict.get("additional_info_needed", "")
                return tasks_completed, final_response, additional_info_needed
            else:
                raise json.JSONDecodeError("Invalid JSON format", response_text, 0)
        except (json.JSONDecodeError, KeyError) as e:
            print("Error parsing response:", e)
            return False, "", "I apologize, but I couldn't generate a proper response. Can you please try rephrasing your request?"

    def run(self, input_data=None):
        if input_data is None:
            input_data = input("User: ")

        conversation_history = ""

        while True:
            # DEBUG: Print input data
            print(f"INPUT DATA: {input_data}")

            delegations = self.delegate_tasks(input_data)
            required_info = self.collect_required_info(delegations, input_data)
            conversation_history += self.process_delegations(delegations, required_info)

            tasks_completed, final_response, additional_info_needed = self.check_task_completion(conversation_history)
            if tasks_completed:
                conversation_history += f"{self.name}: {final_response}\n"
                print(final_response)
                break
            else:
                conversation_history += f"{self.name}: {additional_info_needed}\n"
                print(additional_info_needed)
                input_data = input("User: ")

        return conversation_history