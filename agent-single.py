import os
from dotenv import load_dotenv  # Import the load_dotenv function
import google.generativeai as genai

# Load the environment variables from the .env file
load_dotenv()

# Configure the API with your API key stored in an environment variable
genai.configure(api_key=os.environ["API_KEY"])

# Create a model instance
model = genai.GenerativeModel('gemini-1.0-pro-latest')

prompt = f"""
## System Message:
You are an AI assistant named PlanCraft, designed to help users generate comprehensive and professional business plans.

## Latest Update
The user has indicated his interest in creating a business plan for a music streaming service, and you have determined that paid subscription is the best business model

## Task
Your output should be formatted as a JSON object.

In addition to the standard JSON output, you should also include a "decision" object that indicates the next action to be taken based on your analysis. The "decision" object should have the following structure:

```json
"decision": {{
  "action": "<function_name>",
  "parameters": {{
    "<param_name>": "<param_value>"
  }}
}}
```

The "action" key should specify the function name that the user's code should execute next. The "parameters" object should contain any input parameters required by the specified function.

For example, if you determine that you need more information from the user to generate a comprehensive business plan, you should respond with the following decision object:

```json
"decision": {{
  "action": "AskUser",
  "parameters": {{
    "message": "Please provide more details about your target market, including demographics, psychographics, and buying behaviors."
  }}
}}
```

If you have gathered sufficient information and generated a complete business plan, you should respond with the following decision object:

```json
"decision": {{
  "action": "CompletePlan",
  "parameters": {{}}
}}
```


"""

response = model.generate_content(prompt)
print(response.text)