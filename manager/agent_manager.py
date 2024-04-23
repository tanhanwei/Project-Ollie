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
        # IMPORTANT: Function table must be defined for GEMINI API to call them!
        self.functions = {
            'delegate_to_steam_agent': self.delegate_to_steam_agent,
            'delegate_to_reddit_agent': self.delegate_to_reddit_agent,
            'summarize_agents_responses': self.summarize_agents_responses,
            'respond_to_user':self.respond_to_user,
            'chat_with_data':self.chat_with_data
        }
        self.model = genai.GenerativeModel(model_name='gemini-1.0-pro', tools=self.functions.values())
        self.user_input = ""
        self.first_conversation = True
        self.chat = self.model.start_chat(enable_automatic_function_calling=True)

    def discover_agent_modules(self) -> List[str]:
        agent_modules = []
        agents_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "agents")
        for file in os.listdir(agents_dir):
            if file.endswith(".py") and file != "__init__.py" and file != "agent_base.py":
                agent_modules.append(file[:-3])
        return agent_modules

    def delegate_to_steam_agent(self, query: str):
        """
        Delegate the task to the steam agent.
        
        Args:
            query: instruction for steam agent to analyze a game. Must include a game's name.
        Returns:
            str: the status of the analysis.
        """
        print("MANAGER AGENT: DELEGATING TO STEAM AGENT")
        steam_agent = next((agent for agent in self.agents if agent.__class__.__name__.lower() == "steamagent"), None)
        if steam_agent:
            response = steam_agent.generate_response(query)
            self.data_store["steam_response"] = response
            self.delegated_agents.append("steam_agent")
            return f"Steam Agent: {response}"
        else:
            return "Steam agent not found."

    def delegate_to_reddit_agent(self, query: str):
        """
        Delegate the task to the reddit agent.
        
        Args:
            query: instruction for reddit agent to analyze a topic.
        Returns:
            str: the status of the analysis.
        """
        print("MANAGER AGENT: DELEGATING TO REDDIT AGENT")
        reddit_agent = next((agent for agent in self.agents if agent.__class__.__name__.lower() == "redditagent"), None)
        if reddit_agent:
            response = reddit_agent.generate_response(query)
            self.data_store["reddit_response"] = response
            self.delegated_agents.append("reddit_agent")
            return f"Reddit Agent: {response}"
        else:
            return "Reddit agent not found."

    def summarize_agents_responses(self):
        """
            Summarize all agents' responses AFTER they generated analysis.
            
            Args:
                instruction: instruction to write a detailed analysis, summarize and make a conclusion based on all agents' responses.
            Returns:
                str: the status of the agents' responses.
        """
        print("MANAGER AGENT: ATTEMPTING TO SUMMARIZE...")
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

        # if there's only 1 agent
        if len(agent_responses) == 1:
            print("MANAGER AGENT: Copying data from single agent...")
            agent_response =  agent_responses[0]
            with open(f"{output_folder}/response.json", 'w') as file:
                json.dump(agent_response, file)
            self.task_completed = True
            return f"Analysis generated by MANAGER AGENT, and it is available at {output_folder}/response.json"
        else:
            prompt = f"{instruction}\n\nUser Input: {self.user_input}\n\nAgent Responses:\n"
            for i, response in enumerate(agent_responses, start=1):
                prompt += f"Agent {i}: {response}\n"
                
            response = self.pro_generate_analysis(prompt, output_folder)
            # pro_model = genai.GenerativeModel('gemini-1.5-pro-latest')
            # print("MANAGER AGENT: Summarizing everything...")
            # print(f"MANAGER AGENT: Prompt for summary:\n\n{prompt}")
            # response = pro_model.generate_content(prompt)
            # with open(f"{output_folder}/response.json", 'w') as file:
            #     json.dump(response.text, file)
        

        return response
    def respond_to_user(self, message: str):
        """
        By default, if there are no suitable or available function, respond to the user directly based on user input.
        OR
        After retrieving analysis, share the analysis with the user.

        Args:
            message: your response to the user.
        Returns:
            str: Your response back to the user.
        """
        print(f"MANAGER AGENT: ATTEMMPTING TO RESPOND TO USER like this: {message}")
        self.task_completed = True
        return message
    
    def chat_with_data(self, message: str):
        """
        Generate response based on the data from response.json created earlier. This function can only be called after summarize_agents_responses has been called. User get to ask questions or chat with data.

        Args:
            message: user's chat input
        Returns:
            str: response back to the user.
        """
    
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
        response = self.execute_function_sequence(self.model, self.functions, prompt, self.chat)

        print("MANAGER: EXECUTED FUNCTIONS")


        return response

    