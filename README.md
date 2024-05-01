## Inspiration
I work as a Senior Game Designer for Tencent's Lightspeed Studio, and I had a very helpful game designer intern who is very knowledgable and often perform game related research and analysis for the team. He was someone reliable and can process large amount of data, and gives the team some interesting insights and learning points. When the Google AI Hackathon started, his internship ended, which was a loss for me and the team. So, I thought why not build an agent system that mimics the way I delegate tasks to my intern?

During his internship, we did competitive analysis quite often, and he would gather steam reviews and reddit comments about specific games that we're studying. So, I attempted to build a "game designer" agent that can do all that, which was very challenging because it was hard to build an all-in-one agent.

Then, I had an idea of breaking down into mini agents that specialize in only one tiny area, and I, as the manager, can delegate tasks to these mini agents, and they would get back to me with write-ups, reports and analysis. Then, I, the manager can take a look at everything and learn something from it. That's when I realised that I could build a multi-agent system that mimics the way I delegate tasks at work. At the same time, I also realised that this multi-agent system is not only useful for game research, it can be used for any other fields!


## Vision
With the realization of the great potential and usability of this multi-agent system, I have the vision to build a plug-and-play multi-agent system where any developers can write and use their own agent class easily without touching the source code.

In addition, I also want to make this system very accessible to literally anyone, who may not be a developer, not comfortable to code. And that's why I also built a mini Gemini Agent that can generate another mini Gemini Agents, which is an experimental feature for anyone to tinker around to build their own agents.

## What it does
At work, when my intern finishes a task (which is normally a write-up, report or analysis), he would get back to me with a write up by telling me where is the document and often tell me the gist and the status of the write up verbally in person.

Likewise, Mini Geminis does the same too. An Agent Manager will delegate tasks to relevant Agents, and these mini Gemini Agents will generate a response (a full analysis, summary, or report) and store them as markdown documents, and will reply the agent manager with the status of the tasks and where the responses are stored. Lastly, the Agent Manager will look through everything and make another full report and summary, store the respond as a markdown file, and reply to the user with an answer or general reponse.

Then, the user can also ask follow-up questions based on these markdown files and the agent manager will answer accordingly. If the agent Manager does not have an answer, it will initiate delegations again to get a more concrete answer.

## How we built it
The core of the Mini Gemini system consists of:
1. **Agent Base:** Through this base class, all mini agents (including the agent manager) inherit the Gemini model instance along with their own function tables, which is required for Gemini to respond by requesting a function call automatically as stated in: https://github.com/google-gemini/cookbook/blob/main/quickstarts/Function_calling.ipynb
2. **Agent Manager:** This mini Gemini agent only specialise in 1 task: delegating tasks to other mini Gemini agents and respond back to the user based on the result of the delegation.
3. **Agents:** Each of these mini Gemini Agents specialise in 1 area or task, and they all follow a specific Agent Class Template that allows anyone to create their own agents easily without the need to tinker with any other codes. All Agents are plug-and-play and can support external libraries as well. To demonstrate agents' capability, I have developed reddit, steam and web search agents.
4. **Code Generator Agent:** This is a special type of agent that specilise in generating new agents based on user input. It will also follow the Agent Class Template strictly and create new Agent Class files with a prefix "g_". For example, by asking it to "Create a new wikipedia agent", it will generate a "g_wikipedia_agent.py" and store it in the "/agents" directory of the project.
5. **Agent Registry:** Since is the heart and soul of the plug-and-play system, because it is responsible for all auto agent class imports and also also installation of any additional libraries required by new agent classes.

## Challenges we ran into
1. **Limited usage of Gemini 1.5 Pro:** At the beginning of the project, I realised that there is a very low rate limit to use the powerful Gemini 1.5 Pro for free, and was very concerned whether the 1.0 version is smart enough to handle agent tasks. However, by breaking agent tasks into very small tasks, even Gemini 1.0 Pro handled very well. Therefore, Gemini 1.5 Pro is only used to process large amount of text such as thousands of reviews, website texts, etc.
2. **Personal Skills:** I wouldn't call myself a developer, my core skills are video production, product management, and game design. I can code in Python a little, but crafting the entire architecture and system from scratch was a very challenging task for me, and I rebuild the whole system 5 times during the hackathon, and I kept them all inside the "Archive" folder.
3. **Project Complexity and Priorities:** This project can easily grow into a large-scale project with powerfully crafted mini Gemini agents that can do a lot of tasks. For example, How stable is the system? How far should we improve the agents? How convenient should the plug-and-play be? Is it possible to generate new agents using Gemini? These were some of the tough question that I had to answer.


4. **Frontend:** TO be honest, 90% of the time was spent on backend during the hackathon. Frontend, UI, and design are not my forte. Initially I only wanted to submit only the python codes. But since I want to make it very easy to use and accessible, I thought I should package the entire thing nicely with a simple frontend as well. Thankfully, I got my friend Varun to help me out.

## Accomplishments that we're proud of
Regardless of the outcome of the hackathon, we're very proud of the fact that we can meet the top 3 priorities and deliver on time:
    - **Demonstrate the potential of its architecture** i.e, a manager delegating tasks to other agents, and multiple agents can work together to craft good answers and response to the user with detailed write-ups. 
    - **Show the flexibility and scalability of the system** by ensuring that the plug-and-play feature works perfectly during the hackathon period.
    - **Demonstrate the potential of Agent Generator**, because I believe that this can be a huge community project. If one can easily generate a new agent, I can't imagine the possibilities!

The whole project is a personal achievement for me, because I have never really worked with Python classes before. In terms of its usability, I'm happy with the result so far and I will be using it for my work as well. As for the frontend, we are also happy to solve some of the UI issues and ensuring that the UI is clean and easy to understand.

## What we learned
These are some key takeaways:
1. Interestingly, Gemini can understand, and call multiple functions in sequence on its own before responding to the user using its Automatic Function calling feature.
2. The quality of the response provided by the Mini Geminis system is actually much better than one-shot chatbots such as Claude and ChatGPT, even thpugh it takes longer time to respond.
3. It's possible to generate a new agent in one-shot using the Code Generator Agent. Of course, sometimes it's not perfect and require some editing and fine-tuning, but I think it's a great starting point to realize the potential of a system that can grow its own capabilities.

## What's next for Mini Geminis
I believe that this project is just the beginning of a modular plug-and-play multi-agent system, and there are still so much to work to make the whole thing better, more usable, and shareable. The following are areas that I will look into after this hackathon:
    - **Complex Tasks Capability:** At the moment, all Gemini Agents can only do simple and straightforward tasks. On an agent level, it is still considered a one-shot approach, and this system consists of multiple one-shot tasks that give a better response than a typical chatbot. For example, when a task is delegated to the Web Search Agent, it doesn't really "think" much and figure out what are the best keyword combinations before performing a search (Perhaps I can make a keyword agent?). It also doesn't know how to filter and shortlist relevant webpages before analysing (maybe a filter agent?).
    - **Async and Simultaneous Agent Task Response:** I have no idea how to do async with Python at the moment, so that all agents' task can be performed simultaneously. For now, all agents' tasks are handled sequentially, which can be time consuming.
    - **Multi-Layered Manager-Agent System:** Right now, there is only 1 agent manager that delegates tasks to other agents. I think the whole system will be even more robust if I can include clusters of manager-agent that can receives delegation and delegate tasks to other agents as well. For example, imagine a general manager who delegates to other managers such as business analysis manager agent, market analysis manager agent, etc to craft an entire business plan.