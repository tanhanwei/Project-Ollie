import logging
from manager.agent_manager import AgentManager

def main():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    agent_manager = AgentManager()
    agent_keys = ['reddit_agent']
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