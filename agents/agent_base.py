from abc import ABC, abstractmethod
import google.generativeai as genai
from google.protobuf.struct_pb2 import Struct
import google.ai.generativelanguage as glm

class AgentBase(ABC):
    def __init__(self):
        self.model = genai.GenerativeModel(model_name='gemini-1.0-pro')
        self.task_completed = False
        self.messages = []

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        pass

    def execute_function_sequence(self, model, functions, prompt):
        print("EXECUTING FUNCTION!")
 
        self.messages.append({'role': 'user', 'parts': [f'{prompt}']})
        while not self.task_completed:
            print(f"Generating response using the following prompt:\n\n{self.messages}")
            response = model.generate_content(self.messages)
            print(f"RESPONSE FROM MODEL:\n\n {response}")
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'function_call'):
                    function_call = part.function_call
                    if function_call.args is None:
                        continue
                    result = self.call_function(function_call, functions)
                    s = Struct()
                    s.update({'result': result})
                    function_response = glm.Part(
                        function_response=glm.FunctionResponse(name=function_call.name, response=s))
                    self.messages.append({'role': 'model', 'parts': [part]})
                    self.messages.append({'role': 'user', 'parts': [function_response]})
                else:
                    print("NO FUNCTION CALL. APPENDING TEXT:")
                    self.messages.append({'role': 'model', 'parts': [{'text': getattr(part, 'text', 'No text available')}]})
                    return self.messages
        return self.messages

    def call_function(self, function_call, functions):
        function_name = function_call.name
        if function_call.args is None:
            return "Error: No arguments provided"
        function_args = {k: v for k, v in function_call.args.items()}
        return functions[function_name](**function_args)
    