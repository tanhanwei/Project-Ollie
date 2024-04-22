from agents.manager_agent import ManagerAgent

class MarketAnalysisAgent(ManagerAgent):
    def __init__(self, name, expertise, function_table, managed_agents):
        prompt_file = "prompts/market_analysis_agent_prompt.txt"
        with open(prompt_file, "r") as file:
            prompt = file.read()
        super().__init__(name, expertise, function_table, prompt, managed_agents)
        
    def get_required_info(self):
        return [
            "industry",
            "product_service_description",
            "target_market_location",
            "target_market_demographics",
            "known_competitors",
            "competitive_factors",
            "emerging_trends",
            "regulatory_considerations",
            "additional_notes"
        ]

    def generate_response(self, task_info):
        print("GENERATING RESPONSE...")
        # Perform market analysis based on the provided task_info
        # ...
        response = f"Market Analysis Results:\n{task_info}"
        return response