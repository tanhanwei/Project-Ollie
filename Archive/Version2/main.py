# main.py

import json
import re
from agents.master_agent import MasterAgent
from utilities.function_table import function_table
from utilities.agent_registry import create_agent_registry
from llm_api import call_google_llm_api
from colors import Colors

def main():
    # Create the agent registry
    agent_registry = create_agent_registry(function_table)

    # Create the MasterAgent instance
    master_agent = MasterAgent(
        "Master Agent",
        "Task Delegation",
        function_table,
        list(agent_registry.values())
    )

    print("Welcome to the Multi-Agent System!")
    print("You are now interacting with the Master Agent.")
    
    # Start the interaction loop
    master_agent.run()

if __name__ == "__main__":
    main()