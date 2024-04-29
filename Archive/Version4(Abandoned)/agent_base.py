from abc import ABC, abstractmethod
import google.generativeai as genai
from google.protobuf.struct_pb2 import Struct
import google.ai.generativelanguage as glm
import json

class AgentInterface:
    """
    An interface that defines the common methods and properties for all agent classes.
    """

    @abstractmethod
    def __init__(self, model, output_path):
        """
        Initialize the agent with the provided model and output path.
        
        Args:
            model: The generative model to be used by the agent.
            output_path: The path where the agent's output will be stored.
        """
        pass

    @property
    @abstractmethod
    def name(self):
        """
        Return the name of the agent.
        """
        pass

    @property
    @abstractmethod
    def description(self):
        """
        Return a description of the agent's capabilities and purpose.
        """
        pass

    @abstractmethod
    def generate_response(self, prompt):
        """
        Generate a response based on the provided prompt.
        
        Args:
            prompt: The input prompt for generating the response.
        
        Returns:
            The generated response.
        """
        pass

class AgentBase(ABC):
    def __init__(self, model, output_path):
        self.model = model
        self.output_path = output_path
        self.task_completed = False
        self.messages = []

    @property
    @abstractmethod
    def name(self):
        pass

    @property
    @abstractmethod
    def description(self):
        pass

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        pass

    # def execute_function_sequence(self, model, functions, prompt, chat):
    #     # manual handle
    #     self.task_completed = False

    #     while not self.task_completed:
    #         print("Generating response...")
    #         response = chat.send_message(prompt)
    #         print(f"DEBUG: {__name__}: {response}")

    #         if response.candidates[0].content.parts[0].function_call:
    #             function_call = response.candidates[0].content.parts[0].function_call
    #             function_name = function_call.name
    #             function_args = function_call.args

    #             if function_name in functions:
    #                 result = functions[function_name](**function_args)
    #                 print(f"Function '{function_name}' executed with result: {result}")
    
    #                 # self.task_completed = True
    #                 return result
    #             else:
    #                 print(f"Function '{function_name}' not found in the function table.")
    #                 break
    #         else:
    #             print(f"No function call found in the response.")
    #             return response.candidates[0].content.parts[0].text

    #     return None

    def execute_function_sequence(self, model, functions, prompt, chat):
        # auto handle
        self.task_completed = False

        while not self.task_completed:
            print("Generating response...")
            response = chat.send_message(prompt)
            print(f"DEBUG: MANAGER: {response}")
            self.task_completed = True
            return response.text
    
    def pro_generate_analysis(self, summary_prompt, output_folder):
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        response = model.generate_content(summary_prompt)
        print(response)
        
        try:
            response = model.generate_content(
                summary_prompt,
                safety_settings={
                    'HATE': 'BLOCK_NONE',
                    'HARASSMENT': 'BLOCK_NONE',
                    'SEXUAL': 'BLOCK_NONE',
                    'DANGEROUS': 'BLOCK_NONE'
                }
            )

            if hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
                print("Prompt was blocked due to the following reason:", response.prompt_feedback.block_reason)
                return "Unable to generate analysis due to content restrictions."

            if response.text:
                analysis_text = response.text
                with open(f"{output_folder}/response.json", 'w') as file:
                    json.dump(analysis_text, file)

                print(f"REDDIT AGENT: Completed analysis and saved the result to {output_folder}/response.json")
                self.task_completed = True
                return f"Analysis generated, and it is available at {output_folder}/response.json"
            else:
                print("No useful response was generated. Review the input or model configuration.")
                return "An error occurred during analysis."

        except Exception as e:
            self.task_completed = True
            print("An unexpected error occurred:", str(e))
            return "Failed to generate analysis due to an error."
        finally:
            # Ensures that task_completed is always set to True regardless of how the function exits
            self.task_completed = True