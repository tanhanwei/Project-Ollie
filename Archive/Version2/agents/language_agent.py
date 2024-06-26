from .agent import Agent

class LanguageAgent(Agent):
    def __init__(self, name, expertise, function_table):
        prompt_file = "prompts/language_agent_prompt.txt"
        with open(prompt_file, "r") as file:
            prompt = file.read()
        super().__init__(name, expertise, function_table, prompt)
        
    def generate_response(self, task):
        # Generate a response for language-related tasks
        if "translate" in task.lower():
            # Extract the text and target language from the task and translate
            parts = task.split("translate", 1)[1].strip().split("to")
            text = parts[0].strip().strip("'\"")
            target_lang = parts[1].strip()
            translated_text = self.execute_function("translate", text, target_lang)
            return f"The translation of '{text}' to {target_lang} is: {translated_text}"
        else:
            return "I can assist with language translation. Please provide the text and target language."