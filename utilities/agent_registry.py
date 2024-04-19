# utilities/agent_registry.py

from agents.math_agent import MathAgent
from agents.language_agent import LanguageAgent
from agents.market_analysis_agent import MarketAnalysisAgent
from agents.executive_summary_agent import ExecutiveSummaryAgent
from agents.data_collection_agent import DataCollectionAgent
from agents.risk_analysis_agent import RiskAnalysisAgent

def create_agent_registry(function_table):
    math_agent = MathAgent("Math Agent", "Mathematics", function_table)
    language_agent = LanguageAgent("Language Agent", "Language", function_table)
    executive_summary_agent = ExecutiveSummaryAgent("Executive Summary Agent", "Executive Summary", function_table)
    data_collection_agent = DataCollectionAgent("Data Collection Agent", "Data Collection", function_table)
    risk_analysis_agent = RiskAnalysisAgent("Risk Analysis Agent", "Risk Analysis", function_table)

    market_analysis_agent = MarketAnalysisAgent(
        "Market Analysis Agent",
        "Market Analysis",
        function_table,
        [executive_summary_agent, data_collection_agent, risk_analysis_agent]
    )

    agent_registry = {
        "Math Agent": math_agent,
        "Language Agent": language_agent,
        "Market Analysis Agent": market_analysis_agent,
        "Executive Summary Agent": executive_summary_agent,
        "Data Collection Agent": data_collection_agent,
        "Risk Analysis Agent": risk_analysis_agent
    }

    return agent_registry