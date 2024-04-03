from .agent import Agent
from llm_api import call_google_llm_api
import json

class MathAgent(Agent):
    def generate_response(self, task):
        # Generate a response for math-related tasks
        if "calculate" in task.lower():
            # Convert the natural language task to a mathematical expression
            expression = self.convert_to_expression(task)
            print(f"EXPRESSION: {expression}")
            if expression:
                try:
                    result = eval(expression)
                    return f"The result of {expression} is: {result}"
                except (SyntaxError, ZeroDivisionError, NameError, TypeError, ValueError):
                    return "Invalid mathematical expression. Please provide a valid expression."
            else:
                return "I couldn't extract a valid mathematical expression from the task. Please rephrase it."
        else:
            return "I can assist with mathematical calculations. Please provide a valid expression."

    def convert_to_expression(self, task):
        # Call the Google LLM API to convert the natural language task to a mathematical expression
        prompt = f"""
    Convert the following natural language task to a mathematical expression and respond in JSON format:

    Task: {task}

    Respond with a JSON object in the following format:
    {{
    "expression": "<mathematical_expression>",
    "description": "<optional_description_or_explanation>"
    }}

    Make sure to include only the JSON object in your response, without any additional text or explanations.

    Example:
    Task: Calculate the square root of 64
    Response:
    {{
    "expression": "64 ** 0.5",
    "description": "The square root of 64 can be calculated using the exponentiation operator (**) with an exponent of 0.5."
    }}

    JSON Response:
    """

        response = call_google_llm_api(prompt)
        if response:
            try:
                response_data = json.loads(response)
                expression_data = json.loads(response_data["response"])
                return expression_data["expression"]
            except (json.JSONDecodeError, KeyError):
                return None
        else:
            return None