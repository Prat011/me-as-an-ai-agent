from google.adk import Agent
from custom_tools.tools import web_tools
from custom_agents.slack_agent import slack_agent
from custom_agents.twitter_scroller_agent import twitter_scroller_agent
from custom_agents.agent_planner_agent import agent_planner_agent
from custom_agents.tweet_draft_agent import tweet_draft_agent
from custom_agents.github_agent import github_agent
from custom_agents.tweet_poster import tweet_poster_agent
from custom_agents.video_recording import video_recording_agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types 
from google.adk.tools.agent_tool import AgentTool


main_agent = Agent(
    name='Main_Agent',
    instruction="""You are the central orchestrator for an automated content creation and promotion pipeline. Follow this workflow:

**Phase 1: Trend-Driven Agent Development**
1. Activate `Twitter_Scroller_Agent`: Task it to scroll through recent tweets (e.g., 1000-2000) and identify the top 10 tweets related to AI, based on likes and views.
2. Engage `Agent_Planner_Agent`: Provide it with the list of top 10 AI tweets. Its goal is to decide what new agent/tool to build, define its functionality, and specify the necessary framework, tools, and LLM.
3. Manage Code Development and PR: Based on the plan from `Agent_Planner_Agent`, utilize the `Github_Agent` to create necessary commits for the new agent's code and then to create a pull request for review. (The actual code generation for the agent itself might be handled by tools available to `Github_Agent` or through direct interaction if you have coding capabilities).
4. Notify via `Slack_Agent`: Once the PR is created by `Github_Agent`, use `Slack_Agent` to send a notification. This message should state that the new agent is ready, include the PR link, and remind that a video needs to be recorded for it.

**Phase 2: Video Promotion**
1. Receive Video Path: Await the path to a newly recorded video.
2. Draft Tweet with `Tweet_Draft_Agent`: Once the video path is available, pass it to `Tweet_Draft_Agent` to create a promotional tweet.
3. Post Tweet via `Tweet_Poster_Agent`: Instruct `Tweet_Poster_Agent` to post the drafted tweet. This involves it pinging the Typefully link on Slack for final posting.

Throughout the process, use `web_tools` as needed for research or information gathering.""",
    description='The primary orchestrator agent that coordinates all other custom agents to manage the end-to-end workflow.',
    tools=[
        AgentTool(agent=slack_agent),
        AgentTool(agent=twitter_scroller_agent),
        AgentTool(agent=agent_planner_agent),
        AgentTool(agent=tweet_draft_agent),
        AgentTool(agent=github_agent),
        AgentTool(agent=tweet_poster_agent),
        AgentTool(agent=video_recording_agent)
    ] + web_tools,
    model='gemini-2.0-flash'
)


session_service = InMemorySessionService()

APP_NAME = "money_manager_agent"
USER_ID = "user_1"
SESSION_ID = "session_001" 

session = session_service.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID
)
print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")


runner = Runner(
    agent=main_agent, 
    app_name=APP_NAME,   
    session_service=session_service 
)
print(f"Runner created for agent '{runner.agent.name}'.")


async def call_agent_async(query: str, runner, user_id, session_id):
  """Sends a query to the agent and prints the final response."""
  print(f"\n>>> User Query: {query}")

  content = types.Content(role='user', parts=[types.Part(text=query)])

  final_response_text = "Agent did not produce a final response." # Default

  async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):

      if event.is_final_response():
          if event.content and event.content.parts:
             final_response_text = event.content.parts[0].text
          elif event.actions and event.actions.escalate: 
             final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
          break 

  print(f"<<< Agent Response: {final_response_text}")


async def run_conversation():
    user_query = input("Enter your query: ") # Prompt the user for input
    await call_agent_async(user_query, # Use the user's input
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID)


import asyncio
if __name__ == "__main__":
    try:
        asyncio.run(run_conversation())
    except Exception as e:
        print(f"An error occurred: {e}")
