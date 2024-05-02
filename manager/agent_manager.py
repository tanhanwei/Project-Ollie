print(dir())
import os
import importlib
import pkgutil
from typing import List, Dict
from agents.agent_base import AgentBase
from utils.agent_registry import discover_agents
from dotenv import load_dotenv
from flask_socketio import SocketIO, emit



import google.generativeai as genai
import json
import logging

load_dotenv()
genai.configure(api_key=os.environ["API_KEY"])
output_folder = "output/manager_agent"
os.makedirs(output_folder, exist_ok=True)

from utils.file import File
from app_constants import RESPONSE
response_path = f"{output_folder}/{RESPONSE}"

DELEGATE_PROMPT_DEBUG = False

class AgentManager(AgentBase):
    def __init__(self):
        self.functions = self.get_functions()  # Define self.functions before calling super().__init__()
        super().__init__()
        self.agent_classes = discover_agents()
        print(f"LOADED AGENTS: {self.agent_classes}")
        self.agents = {}
        self.data_store = {}
        self.delegated_agents = []
        self.code_generator_enabled = False



    def get_functions(self):
        return {
            'delegate_task': self.delegate_task,
            'summarize_agents_responses': self.summarize_agents_responses,
            'get_active_agents':self.get_active_agents,
            'retrieve_data_from_agents': self.retrieve_data_from_agents,
            'get_all_agents': self.get_all_agents
            #'chat_with_data': self.chat_with_data
        }

    # def set_agents(self, agent_keys):
    #     """
    #     Initialize and set the agents based on the provided agent keys, and then init the Gemini model.
    #     """
    #     for agent_key in agent_keys:
    #         agent_class = self.agent_classes.get(agent_key)
    #         if agent_class:
    #             self.agents[agent_key] = agent_class()
    #             print(f"Initialized {agent_key} agent.")
    #         else:
    #             print(f"No agent found for key: {agent_key}")
    def set_agents(self, agent_keys):
        """
        Initialize and set the agents based on the provided agent keys, and then init the Gemini model.
        If the code generator agent is in the agent_keys list, enable the code generator and disable all other agents.
        """
        self.code_generator_enabled = 'code_generator_agent' in agent_keys

        for agent_key in agent_keys:
            if agent_key == 'code_generator_agent':
                if self.code_generator_enabled:
                    agent_class = self.agent_classes.get(agent_key)
                    if agent_class:
                        self.agents[agent_key] = agent_class()
                        print(f"Initialized {agent_key} agent.")
                        # Disable all other agents
                        self.agents = {agent_key: self.agents[agent_key]}
                        print("Code Generator Agent is enabled. All other agents are disabled.")
                        break
                    else:
                        print(f"No agent found for key: {agent_key}")
            else:
                if not self.code_generator_enabled:
                    agent_class = self.agent_classes.get(agent_key)
                    if agent_class:
                        self.agents[agent_key] = agent_class()
                        print(f"Initialized {agent_key} agent.")
                    else:
                        print(f"No agent found for key: {agent_key}")





         

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

    # NOTE: Unable to dynamically modify docstring
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
            self.emit_debug_message(f"MANAGER AGENT: @{agent} {instruction}", "MANAGER AGENT")
            if agent in self.agents:
                agent_response = self.agents[agent].generate_response(instruction)
                self.data_store[f"{agent}_response"] = agent_response
                agent_responses.append(f"{agent.capitalize()} Agent: {agent_response}")
            else:
                agent_responses.append(f"No agent found for key: {agent}.")

        self.delegated_agents = agents  # Update delegated_agents to include all the current agents

        print(f"AGENT MANAGER: Delegated AGENTS:\n\n{self.delegated_agents}\n\n")

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
        self.emit_debug_message(f"MANAGER AGENT: Received reports from all agents. Consolidating everything now...", "MANAGER AGENT")
        agent_responses = []
        for agent in self.delegated_agents:
            response_file_path = f"output/{agent}/{RESPONSE}"
            if os.path.exists(response_file_path):
                # with open(response_file_path, 'r') as file:
                #     response_data = json.load(file)
                response_data = File.read_md(response_file_path)
                agent_responses.append(response_data)

        if not agent_responses:
            return "No agent responses found for summarization."

        # if there's only 1 agent
        if len(agent_responses) == 1:
            print("MANAGER AGENT: Copying data from single agent...")
            self.emit_debug_message(f"MANAGER AGENT: There's only 1 agent delegate, I'll just copy its report directly.", "MANAGER AGENT")
            agent_response =  agent_responses[0]
            # with open(f"{output_folder}/{RESPONSE}", 'w') as file:
            #     json.dump(agent_response, file)
            File.write_md(agent_response, response_path)
            return f"Analysis generated by MANAGER AGENT, and it is available at {response_path}"
        else:
            prompt = f"{instruction}\n\nUser Input: {self.user_input}\n\nAgent Responses:\n"
            for i, response in enumerate(agent_responses, start=1):
                prompt += f"Agent {i}: {response}\n"

            summary_text = self.pro_generate_analysis(prompt)
            File.write_md(summary_text, response_path)
            self.emit_debug_message(f"MANAGER AGENT: Ok, done!", "MANAGER AGENT")

        return f"Analysis generated by MANAGER AGENT, and it is available at {response_path}"

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
            response_file_path = f"output/{agent}/{RESPONSE}"
            if os.path.exists(response_file_path):
                response_data = File.read_md(response_file_path)
                agent_responses[agent] = response_data
                logging.info(f"Data retrieved for {agent}")
            else:
                logging.warning(f"Response file not found for {agent}: {response_file_path}")
        return agent_responses


    
    def generate_response(self, user_prompt):
        if self.code_generator_enabled:
            code_generator = self.agents["code_generator_agent"]
            code_generator.set_user_prompt(user_prompt)
            response = code_generator.generate_response(user_prompt)
            return response
        else:
            # generate response normally
            self.user_input = user_prompt

            if self.first_conversation:
                agent_descriptions = []
                for agent_key in self.get_active_agents():
                    agent = self.agents[agent_key]
                    description = getattr(agent, 'description', f"No description available for {agent_key} agent.")
                    agent_descriptions.append(f"- {agent_key}: {description}")

                prompt = f"""
                        You are an agent manager who can answer users' questions and delegate tasks to other agents to perform research and analysis on certain topics. Currently, these are the agents available:

                        {' '.join(agent_descriptions)}

                        You can delegate to more than 1 agent. Once the delegation is complete, you can inform the user where is the file saved.

                        If user asks follow up questions about the analysis or summary, you can retrieve_data_from_agents directly without delegating any agents.

                        User: {user_prompt}
                    """
                self.first_conversation = False
            else:
                prompt = f"{user_prompt}"

            # logging.debug(f"Generating response using the following prompt:\n{prompt}")
            response = self.execute_function_sequence(self.model, self.functions, prompt, self.chat)

            return response