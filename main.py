import logging
from manager.agent_manager import AgentManager
from app_constants import RESPONSE
from utils.file import File
from agents.code_generator_agent import CodeGeneratorAgent

CODE_GENERATOR_MODE = False

def main():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    # if CODE_GENERATOR_MODE:
    #     # do something
    #     code_prompt = File.read_md("temp_agent_template_prompt.md")
    #     # user_input = input("You: ")
    #     code_generator_agent = CodeGeneratorAgent()
    #     response = code_generator_agent.generate_and_save_code(code_prompt, "g_chuck_agent.py")
    #     print("Gemini:", response)
    # else:
    agent_manager = AgentManager()
    # agent_keys = ['steam_agent','web_search_agent','reddit_agent', 'chuck_norris_agent', 'code_generator_agent']
    agent_keys = ['steam_agent']
    # agent_keys = ['steam_agent','web_search_agent','reddit_agent', 'chuck_norris_agent']
    agent_manager.set_agents(agent_keys)

    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            logging.info("Exiting chat. Goodbye!")
            break

        try:
            response = agent_manager.generate_response(user_input)
            print("Gemini:", response)
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            break

if __name__ == "__main__":
    main()