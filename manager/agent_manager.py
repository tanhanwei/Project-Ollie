import os
import importlib
import pkgutil
from typing import List, Dict
from agents.agent_base import AgentBase
from agents.steam_agent import SteamAgent
from agents.reddit_agent import RedditAgent
from dotenv import load_dotenv
import google.generativeai as genai
import json
import logging

load_dotenv()
genai.configure(api_key=os.environ["API_KEY"])
output_folder = "output/manager_agent"
os.makedirs(output_folder, exist_ok=True)

DELEGATE_PROMPT_DEBUG = False

class AgentManager(AgentBase):
    def __init__(self):
        super().__init__()
        self.agent_classes = {}
        self.agents = {}
        self.data_store = {}
        self.delegated_agents = []
        self.load_agents()
        self.first_conversation = True

    def load_agents(self):
        """
        Discover and load all agent modules dynamically from the 'agents' directory.
        """
        package = importlib.import_module('agents')
        prefix = package.__name__ + "."
        for _, modname, _ in pkgutil.iter_modules(package.__path__, prefix):
            module = importlib.import_module(modname)
            for attribute_name in dir(module):
                attribute = getattr(module, attribute_name)
                if isinstance(attribute, type) and issubclass(attribute, AgentBase) and attribute is not AgentBase:
                    agent_key = modname.split('.')[-1]
                    self.agent_classes[agent_key] = attribute
                    print(f"Loaded agent class: {agent_key}")

    def set_agents(self, agent_keys):
        """
        Initialize and set the agents based on the provided agent keys, and then init the Gemini model.
        """
        for agent_key in agent_keys:
            agent_class = self.agent_classes.get(agent_key)
            if agent_class:
                self.agents[agent_key] = agent_class()
                print(f"Initialized {agent_key} agent.")
            else:
                print(f"No agent found for key: {agent_key}")
        # self.set_delegate_docstring() #update the docstring based on chosen agents
        self.set_model() # setup the model after function table is set up
    
    # def set_delegate_docstring(self):
    #     agent_list = ', '.join(self.agents.keys())
    #     self.delegate_docstring = f"""
    #     Delegate tasks to relevant agent by giving instructions.
    #     Args:
    #         agent: name of agent. You can choose from: {agent_list}
    #         instruction: the instruction for the agent.
    #     Returns:
    #         str: status of the delegation.
    #     """
    #     self.delegate_task = self.update_docstring(self.delegate_task, self.delegate_docstring)

    # def update_docstring(self, func, new_docstring):
    #     def wrapper(*args, **kwargs):
    #         return func(*args, **kwargs)
    #     wrapper.__doc__ = new_docstring
    #     return wrapper
    
    def set_model(self):
        self.functions = {
            'delegate_task': self.delegate_task,
            'summarize_agents_responses': self.summarize_agents_responses,
            'get_active_agents':self.get_active_agents,
            'retrieve_data_from_agents': self.retrieve_data_from_agents,
            'get_all_agents': self.get_all_agents
            #'chat_with_data': self.chat_with_data
        }
        self.model = genai.GenerativeModel(model_name='gemini-1.0-pro', tools=self.functions.values())
        self.chat = self.model.start_chat(enable_automatic_function_calling=True)
    
    def get_all_agents(self):
        """
        Get the list of all agents, which may or may not be activated
        """
        return list(self.agent_classes.keys())

    def get_active_agents(self):
        """
        Get the list of initialized agents i.e agents that have been activated.
        """
        return list(self.agents.keys())

    def delegate_task(self, agents: List[str], agent_instructions: List[str]):
        """You can delegate the tasks to one or more agents
        Args:
            agents: Example: ['reddit_agent', 'steam_agent', etc]
            agent_instructions: Instructions for each agent. MUST match the length of agents list. You can ask the agents to perform sentiment analysis, look for emerging topics, etc. All instructions must contain the context.
        Returns:
            str: agents response
        """
        if DELEGATE_PROMPT_DEBUG:
            print(f"AGENTS ASSIGNED: {agents} with instructions: {agent_instructions}")
            return "error"
    
        if len(agents) != len(agent_instructions):
            return "Number of agents and instructions should be the same."

        agent_responses = []
        for agent, instruction in zip(agents, agent_instructions):
            print(f"MANAGER: DELEGATING to: {agent} with instruction: {instruction}")
            if agent in self.agents:
                agent_response = self.agents[agent].generate_response(instruction)
                self.data_store[f"{agent}_response"] = agent_response
                agent_responses.append(f"{agent.capitalize()} Agent: {agent_response}")
            else:
                agent_responses.append(f"No agent found for key: {agent}.")

        self.delegated_agents = agents  # Update delegated_agents to include all the current agents

        response = self.summarize_agents_responses()

        # return "\n".join(agent_responses)
        return response

    def summarize_agents_responses(self):
        """
            Summarize all agents' responses AFTER they generated analysis.
            
            Args:
                instruction: instruction to write a detailed analysis, summarize and make a conclusion based on all agents' responses.
            Returns:
                str: the status of the agents' responses.
        """
        # print("MANAGER AGENT: ATTEMPTING TO SUMMARIZE...")
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
        

        return response.text

    def retrieve_data_from_agents(self, agents: List[str]) -> Dict[str, dict]:
        """
        Retrieve data generated by agents.

        Args:
            agents: List of agent names whose responses are to be retrieved.

        Returns:
            Dict[str, dict]: A dictionary containing data generated by agents, with agent names as keys.
        """
        agent_responses = {}
        for agent in agents:
            response_file_path = f"output/{agent}/response.json"
            if os.path.exists(response_file_path):
                try:
                    with open(response_file_path, 'r') as file:
                        response_data = json.load(file)
                        agent_responses[agent] = response_data
                        logging.info(f"Data retrieved for {agent}")
                except json.JSONDecodeError as e:
                    logging.error(f"Failed to decode JSON from {response_file_path}: {e}")
            else:
                logging.warning(f"Response file not found for {agent}: {response_file_path}")
        return agent_responses


    
    def generate_response(self, user_prompt):
        # Reset task completed status whenever it is generating a response
        self.task_completed = False
        self.user_input = user_prompt

        if self.first_conversation:
            agent_descriptions = []
            for agent_key in self.get_active_agents():
                agent = self.agents[agent_key]
                description = getattr(agent, 'description', f"No description available for {agent_key} agent.")
                agent_descriptions.append(f"- {agent_key}: {description}")

            prompt = f"""You are an agent manager who can answer users' questions and delegate tasks to other agents to perform research and analysis on certain topics. Currently, these are the agents available:

    {' '.join(agent_descriptions)}

    You can delegate to more than 1 agent.

    User: {user_prompt}
    """
            self.first_conversation = False
        else:
            prompt = f"{user_prompt}"

        # logging.debug(f"Generating response using the following prompt:\n{prompt}")
        response = self.execute_function_sequence(self.model, self.functions, prompt, self.chat)

        return response