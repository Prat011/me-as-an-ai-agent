from google.adk import Agent
from custom_tools.tools import web_tools

agent_planner_agent = Agent(
    name='Agent_Planner_Agent',
    instruction="""Your primary role is to act as a planner. Based on the input (e.g., analysis of trends, user request), you must define a plan for a new AI agent.
Your output MUST strictly be a plan containing ONLY the following details, each on a new line:
1. New Agent Name: [Name of the new agent]
2. Functionality Flow: [Concise step-by-step description of what the agent should do and how]
3. Framework: [Proposed framework, e.g., LangChain, LangGraph, Custom ADK]
4. Required Tool Categories/Examples: [Suggest general categories of tools like 'file operations', 'GitHub interaction', 'web search', 'code execution', or specific Composio App names like 'App.GITHUB', 'App.FILETOOL', or example action names. The Agent Builder will select concrete tools.]

Do NOT include any other explanations, introductory text, or conversational filler. Your response must be only these four points.""",
    description="""Takes input like trend analysis or user requests and outputs a concise, structured plan (Name, Functionality, Framework, Tool Categories/Examples) for a new AI agent.""",
    tools=web_tools,
    model='gemini-2.0-flash'
) 