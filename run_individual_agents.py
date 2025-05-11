import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Import agents
from custom_agents.slack_agent import slack_agent
from custom_agents.twitter_scroller_agent import twitter_scroller_agent
from custom_agents.agent_planner_agent import agent_planner_agent
from custom_agents.tweet_draft_agent import tweet_draft_agent
from custom_agents.github_agent import github_agent
from custom_agents.tweet_poster import tweet_poster_agent
from custom_agents.video_recording import video_recording_agent
from main_agent import main_agent # Assuming main_agent.py is in the same directory

# Dictionary to map agent names to agent objects
# Add other agents here if needed
available_agents = {
    "slack_agent": slack_agent,
    "twitter_scroller_agent": twitter_scroller_agent,
    "agent_planner_agent": agent_planner_agent,
    "tweet_draft_agent": tweet_draft_agent,
    "github_agent": github_agent,
    "tweet_poster_agent": tweet_poster_agent,
    "video_recording_agent": video_recording_agent,
    "main_agent": main_agent  # The orchestrator agent
}

# Session service
session_service = InMemorySessionService()
APP_NAME = "individual_agent_runner"
USER_ID = "user_cli_runner"
SESSION_ID_COUNTER = 0

async def call_agent_async(query: str, runner, user_id, session_id):
    """Sends a query to the agent and prints the final response."""
    print(f"\n>>> User Query for {runner.agent.name}: {query}")

    content = types.Content(role='user', parts=[types.Part(text=query)])

    final_response_text = f"Agent {runner.agent.name} did not produce a final response." # Default

    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate:
                final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
            break

    print(f"<<< Agent Response from {runner.agent.name}: {final_response_text}")

async def run_selected_agent():
    """Allows user to select an agent by name, provide a query, and run it."""
    global SESSION_ID_COUNTER

    print("Available agents:")
    agent_names = list(available_agents.keys())
    for name in agent_names:
        print(f"- {name}")

    selected_agent_name_input = ""
    while True:
        selected_agent_name_input = input("Enter the name of the agent to run (or type 'exit' to quit): ").strip()
        if selected_agent_name_input.lower() == 'exit':
            print("Exiting.")
            return
        if selected_agent_name_input in available_agents:
            agent_name = selected_agent_name_input
            selected_agent_obj = available_agents[agent_name]
            break
        else:
            print(f"Error: Agent '{selected_agent_name_input}' not found. Please choose from the list above, or type 'exit'.")

    print(f"\nSelected agent: {agent_name}")
    if selected_agent_obj.description:
        print(f"Description: {selected_agent_obj.description}")

    user_query = input(f"Enter your query for {agent_name}: ")

    session_id = f"session_{agent_name}_{SESSION_ID_COUNTER}"
    SESSION_ID_COUNTER += 1

    try:
        session = session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=session_id
        )
        print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{session_id}' for agent '{agent_name}'")
    except Exception as e:
        print(f"Error creating session: {e}")
        return

    runner = Runner(
        agent=selected_agent_obj,
        app_name=APP_NAME,
        session_service=session_service
    )
    print(f"Runner created for agent '{runner.agent.name}'.")

    await call_agent_async(user_query, runner, USER_ID, session_id)

if __name__ == "__main__":
    try:
        asyncio.run(run_selected_agent())
    except KeyboardInterrupt:
        print("\nExecution cancelled by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}") 