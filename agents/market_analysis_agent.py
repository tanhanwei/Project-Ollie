from .agent import Agent

class MarketAnalysisAgent(Agent):
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