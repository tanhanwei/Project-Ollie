import ast
import operator
import math
import json
from .agent import Agent
from llm_api import call_google_llm_api

class MathExpressionEvaluator:
    def __init__(self):
        self.operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow
        }
        self.functions = {
            'sqrt': math.sqrt,
            'log': math.log,
            'log10': math.log10,
            'log2': math.log2,
            'exp': math.exp,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'factorial': math.factorial,
            'pow': math.pow  # Add the 'pow' function
        }

    def evaluate(self, expression):
        try:
            tree = ast.parse(expression, mode='eval')
            return self.eval_node(tree.body)
        except SyntaxError:
            # If the expression contains the 'pow()' function, replace it with '**' and try again
            if 'pow(' in expression:
                expression = expression.replace('pow(', '(').replace(',', '**')
                tree = ast.parse(expression, mode='eval')
                return self.eval_node(tree.body)
            else:
                raise ValueError("Invalid mathematical expression")

    def eval_node(self, node):
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.BinOp):
            left = self.eval_node(node.left)
            right = self.eval_node(node.right)
            return self.operators[type(node.op)](left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = self.eval_node(node.operand)
            return self.operators[type(node.op)](operand)
        elif isinstance(node, ast.Call):
            func_name = node.func.id
            if func_name not in self.functions:
                raise ValueError(f"Unknown function: {func_name}")
            args = [self.eval_node(arg) for arg in node.args]
            return self.functions[func_name](*args)
        else:
            raise TypeError(f"Unsupported node type: {type(node)}")

class MathAgent(Agent):
    def __init__(self, name, expertise, function_table):
        prompt_file = "prompts/math_agent_prompt.txt"
        with open(prompt_file, "r") as file:
            prompt = file.read()
        super().__init__(name, expertise, function_table, prompt)
        self.expression_evaluator = MathExpressionEvaluator()

    def generate_response(self, task):
        # Generate a response for math-related tasks
        if "calculate" in task.lower():
            # Convert the natural language task to a mathematical expression
            expression = self.convert_to_expression(task)
            print(f"EXPRESSION: {expression}")

            if expression:
                try:
                    # Evaluate the expression using the custom expression evaluator
                    result = self.expression_evaluator.evaluate(expression)
                    print(f"RESULT: {result}")  # Debugging message
                    return f"The result of {expression} is: {result}"
                except (ValueError, TypeError) as e:
                    print(f"ERROR: {str(e)}")  # Debugging message
                    return str(e)
            else:
                return "I couldn't extract a valid mathematical expression from the task. Please rephrase it."
        else:
            return "I can assist with mathematical calculations. Please provide a valid expression."
    def get_required_info(self):
        return []

    def convert_to_expression(self, task):
        # Call the Google LLM API to convert the natural language task to a mathematical expression
        prompt = f"""
        Convert the following natural language task to a mathematical expression that can be evaluated using the math library in Python. Respond with a JSON object containing the expression:
        Task: {task}
        Respond with a JSON object in the following format:
        {{ "expression": "<mathematical_expression>" }}
        Make sure to include only the JSON object in your response, without any additional text or explanations.
        Examples:
        Task: Calculate the square root of 64
        Response: {{ "expression": "sqrt(64)" }}
        Task: Calculate the natural logarithm of 10
        Response: {{ "expression": "log(10)" }}
        Task: Calculate log base 10 of 100
        Response: {{ "expression": "log10(100)" }}
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