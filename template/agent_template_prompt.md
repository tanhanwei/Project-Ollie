Please create a Chuck Norris Agent Class based on the template and the reference:

# Template

```python
# g_{agent_name}_agent.py
import os
from dotenv import load_dotenv
from agents.agent_base import AgentBase
import google.generativeai as genai
from utils.file import File
from app_constants import RESPONSE

load_dotenv()
output_folder = f"output/{__name__.split('.')[-1]}"
os.makedirs(output_folder, exist_ok=True)
response_path = f"{output_folder}/{RESPONSE}"

class {AgentName}Agent(AgentBase):
    description = "A brief description of what the {AgentName}Agent does."

    def __init__(self):
        self.data_store = {}
        self.functions = self.get_functions()
        super().__init__()

    def get_functions(self):
        return {
            'function_name_1': self.function_name_1,
            'function_name_2': self.function_name_2,
            # Add more functions as needed
        }

    def function_name_1(self, arg1: str, arg2: int) -> str:
        """
        A brief description of what function_name_1 does.

        Args:
            arg1 (str): Description of arg1. Example: "example value".
            arg2 (int): Description of arg2. Example: 42.

        Returns:
            str: Description of the return value.
        """
        # Function implementation goes here
        result = "Function 1 result"
        return result

    def function_name_2(self, arg1: list) -> dict:
        """
        A brief description of what function_name_2 does.

        Args:
            arg1 (list): Description of arg1. Example: ["item1", "item2"].

        Returns:
            dict: Description of the return value.
        """
        # Function implementation goes here
        result = {"key": "value"}
        return result

    def generate_response(self, prompt: str) -> str:
        """
        Generate a response based on the user's prompt.

        Args:
            prompt (str): The user's prompt.

        Returns:
            str: The generated response.
        """
        if self.first_conversation:
            prompt = f"""
                Based on user input, perform the required tasks.

                User: {prompt}
            """
        result = self.execute_function_sequence(self.model, self.functions, prompt, self.chat)

        # Save the response or data to a file if needed
        File.write_md(result, response_path)

        return result
```

Explanation of the template:

1. The `NewAgent` class inherits from `AgentBase`, ensuring that it has access to the common functionality provided by the base class.

2. The `description` class variable provides a brief description of what the agent does.

3. The `__init__` method calls the parent class constructor using `super().__init__()`.

4. The `get_functions` method returns a dictionary mapping function names to their corresponding method references. This allows the functions to be called by the Gemini API.

5. Each function that can be called by the Gemini API (`function_name_1` and `function_name_2` in this example) has a descriptive docstring that includes:
   - A brief description of what the function does.
   - `Args`: The input arguments, their types, and example values.
   - `Returns`: A description of the return value.

6. The functions that can be called by the Gemini API are included in the `get_functions` method.

7. The `generate_response` method takes a `prompt` as input and generates a response using the `execute_function_sequence` method provided by `AgentBase`. It returns the response as a string.

8. Optionally, the agent can save long results, data, or responses to a file in the `output/{agent_name}/response.md` format.

9. Naming convention must be {something}_agent.py. For example: youtube_agent, recipe_agent, etc.

10. All data MUST be saved externally. Any local data variable such as self.data, self.data_store, etc must be saved externally.

11. Function sequence can be chained so that the final response gives the final answer or summary.

# Reference:

Chuck Norris Jokes Api - JSON API for random Chuck Norris jokes
chucknorris.io is a free JSON API for hand curated Chuck Norris facts. Read more

Subscribe for new Chuck Facts
Enter your email
 
Usage
Retrieve a random chuck joke in JSON format.

https://api.chucknorris.io/jokes/random
Example response:

{
"icon_url" : "https://assets.chucknorris.host/img/avatar/chuck-norris.png",
"id" : "q8fcx7zdQpmpSpiRrEKlxg",
"url" : "",
"value" : "Chuck Norris COULD bench press Rosie O'Donnell."
}
Get me a new one ... (press "r" to refresh)
Retrieve a random chuck norris joke from a given category.

https://api.chucknorris.io/jokes/random?category={category}
Retrieve a list of available categories.

https://api.chucknorris.io/jokes/categories
Free text search.

https://api.chucknorris.io/jokes/search?query={query}
Slack Integration
The Chuck Norris app existed even before slack existed. Start retrieving random Chuck Norris facts by just typing /chuck into your slack console.

Additionally you can type /chuck {category_name} to get a random joke from a given category. Type /chuck -cat to show a list of all available categories.

You can also try the free text search by sending /chuck ? {search_term}.

Fool your coworkers by personalizing your Chuck Facts with /chuck @{user_name}.

Add to Slack
Installation takes just 1 minute!

Help: From within slack, you can just type /chuck help for some extra information on how to use the app.

Facebook Messenger
The Chuck Norris app is also on Facebook Messenger. Click the Message Us button below to start a conversation.

You can simply ask a random joke by typing hi, tell me a joke. To get help to get started type help.

Contact: Feel free to tweet ideas, suggestions, help requests and similar to @matchilling or drop me a line at m@matchilling.com

Privacy: The app was a weekend project and is just fun. All we're storing are team and user ids and the appropriate OAuth tokens. This allows you to post these awesome Chuck Norris facts on slack on the appropriate channel. Our applications is hosted on https://aws.amazon.com/privacy. We use a secure connection between slack servers and aws. We anonymously keep track of two data points; the total number of teams and unique users. None of the data will ever be shared, except for maybe some anonymous statistics in the future.

Chucknorris.io is free and will always be! However, as maintaining this service costs $$$, we are glad to be sponsored by Jugendstil.io.
Twitter GitHub 
Attribution: Artwork "Dancing Chuck" by jesgrad07
Legal disclaimer: This website and its creators are not affiliated with Chuck Norris, any motion picture corporation, any television corporation, parent, or affiliate corporation. All motion pictures, products, and brands mentioned on this website are the respective trademarks and copyrights of their owners. All material on this website is intended for humorous entertainment (satire ) purposes only. The content on this website is not necessarily true and should not be regarded as truth.
Application Privacy Statement Status
