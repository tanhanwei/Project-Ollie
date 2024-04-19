# agents/executive_summary_agent.py

from agents.agent import Agent

class ExecutiveSummaryAgent(Agent):
    def __init__(self, name, expertise, function_table):
        prompt_file = "prompts/executive_summary_agent_prompt.txt"
        with open(prompt_file, "r") as file:
            prompt = file.read()
        super().__init__(name, expertise, function_table, prompt)

    def generate_executive_summary(self, market_analysis_data):
        # Implement the logic to generate an executive summary based on the market analysis data
        # You can use the LLM API or any other method to generate the summary
        # For example:
        prompt = f"Generate an executive summary for the following market analysis data:\n{market_analysis_data}"
        summary = self.generate_response(prompt)
        return summary