from abc import ABC, abstractmethod
import google.generativeai as genai
import json
import logging

class AgentBase(ABC):
    def __init__(self):
        self.messages = []

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        pass

    def execute_function_sequence(self, model, functions, prompt, chat):
        logging.debug(f"Generating response using the following prompt:\n{prompt}")
        response = chat.send_message(prompt)
        logging.debug(f"CHAT HISTORY:\n{chat.history}")
        logging.debug(f"DEBUG: response: \n\n{response}")
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

                print(f"Completed analysis and saved the result to {output_folder}/response.json")
                return f"Analysis generated, and it is available at {output_folder}/response.json"
            else:
                print("No useful response was generated. Review the input or model configuration.")
                return "An error occurred during analysis."

        except Exception as e:
            print("An unexpected error occurred:", str(e))
            print("REDDIT AGENT: Task completed with error.")
            return "Failed to generate analysis due to an error."