import os
import importlib
from typing import List
from agents.agent_base import AgentBase
from dotenv import load_dotenv
import google.generativeai as genai
import json

load_dotenv()
genai.configure(api_key=os.environ["API_KEY"])
output_folder = "output/manager_agent"
os.makedirs(output_folder, exist_ok=True)

class AgentManager(AgentBase):
    def __init__(self):
        super().__init__()
        self.agents = []
        agent_modules = self.discover_agent_modules()
        for module_name in agent_modules:
            module = importlib.import_module(f"agents.{module_name}")
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, AgentBase) and attr != AgentBase:
                    self.agents.append(attr())
        self.data_store = {}
        self.delegated_agents = []
        self.functions = {
            'delegate_to_steam_agent': self.delegate_to_steam_agent,
            'delegate_to_reddit_agent': self.delegate_to_reddit_agent,
            'summarize_agents_responses': self.summarize_agents_responses,
            'respond_to_user':self.respond_to_user
        }
        self.model = genai.GenerativeModel(model_name='gemini-1.0-pro', tools=self.functions.values())
        self.user_input = ""
        self.first_conversation = True

    def discover_agent_modules(self) -> List[str]:
        agent_modules = []
        agents_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "agents")
        for file in os.listdir(agents_dir):
            if file.endswith(".py") and file != "__init__.py" and file != "agent_base.py":
                agent_modules.append(file[:-3])
        return agent_modules

    def delegate_to_steam_agent(self, query: str):
        steam_agent = next((agent for agent in self.agents if agent.__class__.__name__.lower() == "steamagent"), None)
        if steam_agent:
            response = steam_agent.generate_response(query)
            self.data_store["steam_response"] = response
            self.delegated_agents.append("steam_agent")
            return f"Steam Agent: {response}"
        else:
            return "Steam agent not found."

    def delegate_to_reddit_agent(self, query: str):
        reddit_agent = next((agent for agent in self.agents if agent.__class__.__name__.lower() == "redditagent"), None)
        if reddit_agent:
            response = reddit_agent.generate_response(query)
            self.data_store["reddit_response"] = response
            self.delegated_agents.append("reddit_agent")
            return f"Reddit Agent: {response}"
        else:
            return "Reddit agent not found."

    def summarize_agents_responses(self):
        instruction = "You are the master agent that handles user input and delegates tasks to other agents. Now that all agents have completed their tasks, based on all agents' responses below, write a detailed analysis, summarize and make a conclusion as a response to back to the user."
        agent_responses = []
        for agent in self.delegated_agents:
            response_file_path = f"output/{agent}/response.json"
            if os.path.exists(response_file_path):
                with open(response_file_path, 'r') as file:
                    response_data = json.load(file)
                    agent_responses.append(response_data)

        if not agent_responses:
            return "No agent responses found for summarization."

        prompt = f"{instruction}\n\nUser Input: {self.user_input}\n\nAgent Responses:\n"
        for i, response in enumerate(agent_responses, start=1):
            prompt += f"Agent {i}: {response}\n"
        pro_model = genai.GenerativeModel('gemini-1.5-pro-latest')
        response = pro_model.generate_content(prompt)
        with open(f"{output_folder}/response.json", 'w') as file:
            json.dump(response.text, file)
        self.task_completed = True

        return f"Analysis completed by master agent and is available at {output_folder}/response.json"

    def respond_to_user(self, message: str):
        """
        By default, ff there are no suitable or available function, respond to the user directly based on user input.

        Args:
            message: your response to the user.
        Returns:
            str: Your response back to the user.
        """
        self.task_completed = True
        return message
    
    def generate_response(self, user_prompt):
        # Reset task completed status whenever it is generating a response
        self.task_completed = False
        self.user_input = user_prompt

        if self.first_conversation:
            prompt = f"""You are an agent designed specifically to help users to do research on certain topics. Currently, you have access to reddit agents to research on subreddits and steam agent to research on game reviews.
                
                Based on the user input, respond by using the respond_to_user function unless you decide to delegate your task to agents (steam or reddit). You can delegate to both or one of them or respond to the user directly.

                User: {user_prompt}
            """
            self.first_conversation = False
        else:
            prompt = f"{user_prompt}"
        messages = self.execute_function_sequence(self.model, self.functions, prompt)

        print("MANAGER: EXECUTED FUNCTIONS")
        print(f"RESPONSE FROM generate_response:\n\n{messages}")

        response = self.extract_reply_to_user(messages)

        return response

        # if response.candidates and response.candidates[0].content.parts:
        #     return response.candidates[0].content.parts[0].text
        # else:
        #     print("No response generated.")
        #     return "No response generated."
    
    def extract_reply_to_user(self, messages):
        print(f"EXTRACTING REPLY: {messages}")
        reply = None
        for part in messages[-1]['parts']:
            if hasattr(part, 'function_response'):
                result = part.function_response.response['result']
                if isinstance(result, dict) and 'string_value' in result:
                    reply = result['string_value']
                elif isinstance(result, str):
                    reply = result
                break
        print(f"EXTRACTED REPLY: {reply}")
        return reply
    
# TODO: Agent has no memory, generate_response is repeating initial prompt, currently it responding blank message after first response.