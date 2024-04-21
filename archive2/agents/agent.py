class Agent:
    def __init__(self, name, expertise, function_table, prompt):
        self.name = name
        self.expertise = expertise
        self.function_table = function_table
        self.prompt = prompt

    def execute_function(self, function_name, *args, **kwargs):
        if function_name in self.function_table:
            return self.function_table[function_name](*args, **kwargs)
        else:
            raise ValueError(f"Function '{function_name}' not found in the function table")

    def generate_response(self, task):
        # Process the task and generate a response
        # This method can be overridden by specialized agents
        return "I'm not sure how to handle this task."