# code_generator_agent.py
import os
from dotenv import load_dotenv
from agents.agent_base import AgentBase
import google.generativeai as genai
from utils.file import File
from app_constants import RESPONSE

load_dotenv()
output_folder = f"output/{__name__.split('.')[-1]}"
response_path = f"{output_folder}/{RESPONSE}"

class CodeGeneratorAgent(AgentBase):
    description = "An agent that generates Python code based on a given prompt using the Gemini API."

    def __init__(self):
        self.data_store = {}
        self.functions = self.get_functions()
        super().__init__()
        self.code_model = genai.GenerativeModel(model_name='gemini-1.5-pro-latest')
        self.user_long_prompt = ""
        self.can_generate = False
        os.makedirs(output_folder, exist_ok=True)

    def get_functions(self):
        return {
            # 'generate_code': self.generate_code,
            # 'save_code_as_agent': self.save_code_as_agent,
            'generate_and_save_code': self.generate_and_save_code,
            'retrieve_code': self.retrieve_code
        }

    def generate_code(self, prompt: str) -> str:
        """
        Generate Python code based on the given prompt.

        Args:
            prompt (str): The prompt describing the desired code functionality.

        Returns:
            str: The generated Python code.
        """
        # Use the Gemini API to generate code based on the prompt
        self.emit_debug_message("**CODE GENERATOR AGENT:** Generating code...", "CODE GENERATOR AGENT")
        response = self.code_model.generate_content(prompt)
        generated_code = response.text
        print("CODE GENERATOR AGENT: Code generated!")
        return generated_code

    def save_code_as_agent(self, code: str, agent_name: str) -> str:
        """
        Save the generated code as a new agent file.

        Args:
            code (str): The generated Python code.
            agent_name (str): The name of the new agent.

        Returns:
            str: A message indicating the successful creation of the agent file.
        """
        self.emit_debug_message("**CODE GENERATOR AGENT:** Saving code...", "CODE GENERATOR AGENT")
        agent_folder = "agents"
        os.makedirs(agent_folder, exist_ok=True)


        # Remove the backticks and "python" keyword from the code
        code = code.strip("```python").strip("```").strip()

        agent_file = f"{agent_folder}/g_{agent_name}.py"
        with open(agent_file, 'w') as file:
            file.write(code)

        print("CODE GENERATOR AGENT: Code saved!!")
        return f"Agent file 'g_{agent_name}_agent.py' created successfully."
    
    def generate_and_save_code(self, agent_name: str):
        """
            Generate new agent class based on IF AND ONLY IF user asks for it, and save it in the agent directory. 

            Args:
                agent_name: You need to help the user to name the new agent class. For example: reddit_agent, steam_agent, etc.
            Returns:
                str: the full python code
        """
        if self.can_generate:
            print("CODE GENERATOR AGENT: Attempting to generate and save code...")
            agent_template = File.read_md("template/agent_template.md")
            code_generation_prompt = f"""
                Please follow the agent template strictly and generate the full python code with full implementation based on user input.\n\n

                # Agent Template\n\n

                {agent_template}\n\n

                # User Input:\n\n
                {self.user_long_prompt}\n\n

                # NOTE\n\n
                Please respond only with the full python code, and nothing else. No need explanations.
            """
            code = self.generate_code(code_generation_prompt)
            status = self.save_code_as_agent(code, agent_name)
            File.write_md(code, response_path)
            print(f"Code Generator Agent: {status}")
            self.can_generate = False
        else:
            print("NOT ALLOWED TO GENERATE AGAIN")
        return "Done!"
    
    def set_generate_permission(self):
        self.can_generate = True
    
    def set_user_prompt(self, long_prompt: str):
        self.user_long_prompt = long_prompt
        print("CODE GENERATOR AGENT: User original prompt saved!")

    def retrieve_code(self):
        """
            Retrieve previously generated agent code
        """
        self.emit_debug_message("**CODE GENERATOR AGENT:** Code retrieved.", "CODE GENERATOR AGENT")
        code = File.read_md(response_path)
        return code

    def generate_response(self, user_prompt: str) -> str:
        print("CODE GENERATOR AGENT: Received user prompt!")
        """
        Generate a response based on the user's prompt.

        Args:
            prompt (str): The user's prompt.

        Returns:
            str: The generated response.
        """
        self.set_generate_permission()
        if self.first_conversation:
            prompt = f"""
                You are an agent generator that can create Agent Class using provided template. Based on user input, determine agent name (for example: steam_agent.py, reddit_agent.py, etc) and generate the full code. If possible, explain the code to the user as well. Use generate_and_save_code function to write full python code.

                If the user is asking you to generate or create a new agent, you can call generate_and_save_code function.

                YOU ONLY NEED TO GENERATE ONCE.

                If the user is asking anything about the code that you have generated, use retrieve_code function to access the code.

                User: {user_prompt}
            """
        else:
            prompt = user_prompt
        
        result = self.execute_function_sequence(self.model, self.functions, prompt, self.chat)

        # Save the response or data to a file if needed
        
        self.emit_debug_message("**CODE GENERATOR AGENT:** Done!", "CODE GENERATOR AGENT")
        return result