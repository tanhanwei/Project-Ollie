from agents.manager_agent import ManagerAgent

class MasterAgent(ManagerAgent):
    def __init__(self, name, expertise, function_table, managed_agents):
        prompt_file = "prompts/master_agent_prompt.txt"
        with open(prompt_file, "r") as file:
            prompt = file.read()
        super().__init__(name, expertise, function_table, prompt, managed_agents)

    # Add any additional methods or overrides specific to the MasterAgent