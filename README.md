## Inspiration
I work as a Senior Game Designer at Tencent's Lightspeed Studios, and I had a very helpful game designer intern who was knowledgeable and often performed game-related research and analysis for the team. He was reliable, could process large amount of data, and provided the team with interesting insights and learning points. When the Google AI Hackathon started, his internship ended, which was a loss for the team. So, I thought, why not build an agent system that mimics the way I delegate tasks to the intern?

During his internship, we did competitive analysis quite often, and he would gather Steam reviews and Reddit comments about specific games that we were studying. I attempted to build a "game designer" agent that could do all that, but it was challenging to build an all-in-one agent.

Then, I had the idea of breaking it down into specialised agents that take care of the respective specialised areas, and I, as the manager, could delegate tasks to these specialised agents. They would get back to me with write-ups, reports, and analysis, and I could take a look at the findings all at once and learn from it. That's when I realized that I could build a multi-agent system that mimics the way I delegate tasks at work. At the same time, I also realized that this multi-agent system is not only useful for game research but it may also be useful in other areas such as market research, sentiment analysis, academic research etc.

## Vision
With the realization of the great potential and usability of this multi-agent system, I have the vision to build a plug-and-play multi-agent system where any developers can write and use their own agent class easily without touching the source code.

In addition, I want to make this system very accessible to literally anyone, who may not be a developer or comfortable with coding. That's why I built the Code Generator Agent that can generate different types of specialised agent. The Code Generator Agent is an experimental feature for anyone to tinker around and build their own specialised agents.

## What it does

### Task Delegation and Completion
Project Ollie consists of an Agent Manager and specialised agents. The Agent Manager delegates tasks to relevant specialised agents, and these agents generate a response (a full analysis, summary, or report) and store them as markdown documents. They reply to the Agent Manager with the status of the tasks and the location of the responses. When ready, the Agent Manager looks through the findings to generate a final report, stores the final report as a markdown file, and responds to the user with its finalised findings.

The user can ask follow-up questions to the Agent Manager based on the markdown files. If the Agent Manager does not have an answer, it will re-initiate its delegations automatically to attempt to provide an answer. 

### Agent Generation
To encourage user creation of new specialised agents, a simplified feature called the Code Generator Agent is built. The Code Generator Agent creates specialised agents based on user prompt and the Agent Class Template. In addition, the user can include relevant API documentations and even code snippets from other projects in the prompt, and the Code Generator Agent can generate a new python class file, which can be loaded instantly for quick testing.

Based on my own tests, the Code Generator Agent could generate the following simple specialised agents one-shot:

- **Chuck Norris Agent:** Just for fun, I copied and pasted the entire page from https://api.chucknorris.io/ and a fully functional `g_chuck_norris_agent.py` python class file was generated. Note: if you're testing this agent, sometimes it may not work due to Gemini's safety parameters (some jokes are not safe)
- **Wikipedia Agent:** This was generated one-shot without any reference. Interestingly, a new python class `g_wikipedia_agent.py` was generated and it relies on Wikipedia's Python API from PyPI, and a pip install will be triggered automatically to install the missing wikipedia library. The use case here is simple and can be tinkered to enhance its capability.
- **US Trademark Agent:** Another one-shot agent generated by pasting this page into the prompt: https://markerapi.com/
- **arXiv Agent:** This agent can retrieve research papers' summary. All I did was copying and pasting its API documentation. You can test it using this prompt: "Retrieve paper details for 2307.05844". The use case here is simple, but with the base code generated by the Code Generator Agent, it can be easily enhanced with advanced features. 

## How I built it
The core of the Project Ollie consists of:

1. **Agent Base:** Through this base class, all agents (including the Agent Manager) inherit the Gemini model instance along with their own function tables, which is required for Gemini to respond by requesting a function call automatically as stated in the [Function Calling Quickstart](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Function_calling.ipynb).
2. **Agent Manager:** This agent specializes in one task: delegating tasks to other agents and responding back to the user based on the findings.
3. **Agents:** Each of these agents specializes in one area or task, and they all follow a specific Agent Class Template that allows anyone to create their own agents easily without the need to modify the source code. All Agents are plug-and-play and can support external libraries as well. To demonstrate agents' capabilities, I have developed Reddit, Steam, and Web Search Agents.
4. **Code Generator Agent:** This is a special type of agent that specializes in generating new agents based on user prompt. It follows the Agent Class Template and creates new Agent Class files with a prefix "g_". For example, by asking it to "Create a new Wikipedia agent," it will generate a "g_wikipedia_agent.py" agent and store it in the "/agents" directory of the project.
5. **Agent Registry:** This is the heart and soul of the plug-and-play system because it is responsible for all auto agent class imports and the installation of any additional libraries required by new agent classes.

The project utilizes the following technical stack:
- Backend: Python, Flask, Flask-SocketIO
- Frontend: Svelte, Tailwind CSS, DaisyUI
- AI Model: Google Gemini 1.0 Pro and 1.5 Pro

## Challenges I ran into
1. **Limited usage of Gemini 1.5 Pro:** At the beginning of the project, I realised that Gemini 1.5 Pro is powerful but it has very low API rate limit. As for Gemini 1.0, I was concerned on whether it is capable to handle/understand all the agents' tasks. Thankfully, by breaking the agents' tasks into specialised agents' tasks, Gemini 1.0 Pro handled them very well. Therefore, Gemini 1.5 Pro is only used to process large amount of text, such as thousands of reviews, website texts, etc.
2. **Personal Skills:** My core skills are video production, product management, and game design. I have a basic understanding of Python. Crafting the entire architecture and system from scratch was a very challenging task for me. I rebuilt the whole system five times during the hackathon, and I kept them all inside the "Archive" folder.
3. **Project Complexity:** The complexity of this project is that it can grow into a large-scale project with powerfully crafted agents that can perform complex tasks. It can go deep by enhancing the capabilities of the agents or it can showcase many different types of agents. 
5. **Frontend:** To be honest, 95% of the time was spent on the backend during the hackathon. Frontend, UI, and design are not my forte. Initially, I only wanted to submit the Python code. But since I wanted to make it very easy to use and accessible, I thought I should present the entire thing nicely with a simple frontend as well. Thankfully, I got my friend Varun to help me out. We used Svelte for the frontend development, along with Tailwind CSS and DaisyUI for styling. The main challenge was to establish real-time communication between the backend and frontend using Flask-SocketIO to display the agent's status messages as speech bubbles.

## Accomplishments that I'm proud of
Regardless of the outcome of the hackathon, I'm very proud of the fact that I can meet the top three priorities and deliver on time:
- **Demonstrate the potential of Project Ollie's architecture**, i.e., having an Agent Manager to delegate tasks to specialised agents, and multiple specialised agents can work together to craft good answers and responses to the user with detailed findings.
- **Show the flexibility and scalability of Project Ollie** by ensuring that the plug-and-play feature works perfectly during the hackathon period.
- **Demonstrate the potential of Agent Generator** because I believe that this can be a huge community project. If one can easily generate new agents and yield useful findings, I believe it could have meaningful impact in the works of those in many fields such as game design, research, marketing etc.

Project Ollie is a personal achievement for me because I have never really worked with Python classes before. In terms of its usability, I'm happy with the result so far, and I will be using it for my work as well. As for the frontend, I am also happy to solve some of the UI issues and ensure that the UI is clean and user friendly.

## What I learned
These are some key takeaways:
1. Interestingly, it appears that Gemini can understand and call multiple functions in sequence on its own before responding to the user, using its Automatic Function calling feature.
2. The quality of the response provided by Project Ollie is actually much better than one-shot chatbots such as Claude and ChatGPT, even though it takes longer to respond.
3. It's possible to generate a new agent in one shot using the Code Generator Agent. Of course, sometimes it's not perfect and requires some editing and fine-tuning, but I think it's a great starting point to build one's specialised agent. 

## What's next for Project Ollie
I believe that this project is just the beginning of a modular plug-and-play multi-agent system, and there is still so much work to make the whole system better, more usable, and shareable. The following are areas that I will look into after this hackathon:
- **Complex Tasks Capability:** At the moment, all specialised agents can only do simple and straightforward tasks. On an agent level, it is still considered a one-shot approach, and this system consists of multiple one-shot tasks that give a better response than a typical chatbot. For example, when a task is delegated to the Web Search Agent, it doesn't really "think" much and figure out what are the best keyword combinations before performing a search (perhaps creating a keyword agent would be the solution?). It also doesn't know how to filter and shortlist relevant webpages before analysing (maybe a filter agent?).
- **Async and Simultaneous Agent Task Response:** I have no idea how to do async with Python at the moment, so that all agents' tasks can be performed simultaneously. For now, all agents' tasks are handled sequentially, which can be time-consuming.
- **Multi-Layered Manager-Agent System:** Right now, there is only one Agent Manager that delegates tasks to other agents. I think the whole system will be even more robust if I can include clusters of manager-agents that can receive delegation and delegate tasks to other agents as well. For example, imagine a general manager who delegates to other managers, such as a business analysis manager agent and a market analysis manager agent, to craft an entire business plan.
- **Community-Driven Agent Development:** With the Agent Generator feature, I envision a community-driven approach where users can easily generate new agents tailored to their specific needs. This can lead to a vast library of agents covering various domains and functionalities, making the system even more versatile and powerful.


## How to Set Up and Test the Project

Follow these detailed steps to get the project up and running on your local machine.

### Prerequisites

Ensure you have Python, Node.js, and npm installed on your computer. If not, install them from their respective official sites:

- [Python](https://www.python.org/downloads/)
- [Node.js and npm](https://nodejs.org/en/download/)

### Clone the Repository

First, you need to clone the repository to your local machine. Open your terminal and run:

```bash
git clone https://github.com/tanhanwei/Project-Ollie.git
```


### Set Up the Backend

Navigate to the project folder:

```bash
cd your-repository
```

Set up a Python virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the root directory of the project to store your API keys and other sensitive information. Open the file in a text editor and add the following content:

```
API_KEY=<google gemini api key>
REDDIT_CLIENT_ID=***
REDDIT_CLIENT_SECRET=***
REDDIT_USERNAME=***
REDDIT_PASSWORD=***
BRAVE_SEARCH_API_KEY=***
```

Replace the placeholders and asterisks with your actual API keys and credentials.

### Set Up the Frontend

Navigate to the frontend folder:

```bash
cd gemini-client
```

Install the required npm packages:

```bash
npm install vite --save-dev
npm install socket.io-client
```

Build the frontend:

```bash
npm run build
```

### Start the Application

After building the frontend, navigate back to the project root directory:

```bash
cd ..
```

Run the application:

```bash
python app.py
```

### Access the Application

Open a web browser and go to the following URL to access the application:

```
http://127.0.0.1:5000
```

You should now be able to see the application running locally.