from abc import ABC, abstractmethod
import google.generativeai as genai
from google.protobuf.struct_pb2 import Struct
import google.ai.generativelanguage as glm
import json

class AgentBase(ABC):
    def __init__(self):
        # self.model = genai.GenerativeModel(model_name='gemini-1.0-pro')
        self.task_completed = False
        self.messages = []

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        pass

    def execute_function_sequence(self, model, functions, prompt, chat):
        self.task_completed = False

        while not self.task_completed:
            print("Generating response...")
            response = chat.send_message(prompt)
            print(f"TASK COMPLETED: {self.task_completed}")
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
            print("REDDIT AGENT: Task completed with error.")
            return "Failed to generate analysis due to an error."
        finally:
            # Ensures that task_completed is always set to True regardless of how the function exits
            self.task_completed = True