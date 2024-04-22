from manager.agent_manager import AgentManager

def main():
    agent_manager = AgentManager()

    # user_input = "Tell me about the latest discussions on the game called Vampire Survivors."

    while True:
        # Input your message
        user_input = input("You: ")
        # Check if the user wants to exit the chat
        if user_input.lower() in ['exit', 'quit']:
            print("Exiting chat. Goodbye!")
            break

        # Generate a response from the model
        try:
            response = agent_manager.generate_response(user_input)
            print("Gemini:", response)
        except Exception as e:
            print(f"An error occurred: {e}")
            break

if __name__ == "__main__":
    main()