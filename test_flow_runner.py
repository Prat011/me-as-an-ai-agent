import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Import agents (ensure these paths are correct and agents are defined)
from custom_agents.slack_agent import slack_agent
from custom_agents.twitter_scroller_agent import twitter_scroller_agent
from custom_agents.agent_planner_agent import agent_planner_agent
from custom_agents.tweet_draft_agent import tweet_draft_agent
from custom_agents.github_agent import github_agent
from custom_agents.tweet_poster import tweet_poster_agent
from custom_agents.agent_builder import agent_builder_agent
from custom_agents.video_recording import video_recording_agent
# main_agent could also be part of a flow if it can be triggered by a simple text query
from main_agent import main_agent

# Dictionary to map agent names to agent objects
available_agents = {
    "twitter_scroller_agent": twitter_scroller_agent,
    "slack_agent": slack_agent,
    "agent_planner_agent": agent_planner_agent,
    "tweet_draft_agent": tweet_draft_agent,
    "github_agent": github_agent,
    "tweet_poster_agent": tweet_poster_agent,
    "video_recording_agent": video_recording_agent,
    "main_agent": main_agent,
    "agent_builder_agent": agent_builder_agent
}

# Define some example flows
# A flow is a list of agent names (keys from available_agents)
predefined_flows = {
    "1_trend_analysis_to_plan": ["twitter_scroller_agent", "agent_planner_agent", "agent_builder_agent"],
    "2_plan_to_tweet_draft": ["agent_planner_agent", "tweet_draft_agent"],
    "3_full_trend_to_draft": ["twitter_scroller_agent", "agent_planner_agent", "tweet_draft_agent"],
    "4_simple_slack_notification": ["slack_agent"], # Example of a single-agent flow for consistency
}

# Session service and unique ID generation
session_service = InMemorySessionService()
APP_NAME = "agent_flow_tester"
USER_ID = "user_flow_tester"
# Use a dictionary for mutable integer to pass by reference for session ID counter
SESSION_ID_COUNTER = {'val': 0}

async def call_agent_in_flow(agent_obj, query: str, user_id: str, app_name: str, session_service_instance, session_id_counter_ref):
    """Sends a query to a specific agent and returns its final response text."""
    session_id = f"session_flow_{agent_obj.name}_{session_id_counter_ref['val']}"
    session_id_counter_ref['val'] += 1

    print(f"\n>>> Running Agent: {agent_obj.name}")
    print(f"    With Query (first 100 chars): '{query[:100]}{'...' if len(query) > 100 else ''}'")

    try:
        session = session_service_instance.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id
        )
    except Exception as e:
        error_msg = f"Error creating session for {agent_obj.name}: {e}"
        print(f"    <<< {error_msg}")
        return error_msg

    runner = Runner(
        agent=agent_obj,
        app_name=app_name,
        session_service=session_service_instance
    )

    content = types.Content(role='user', parts=[types.Part(text=query)])
    final_response_text = f"Agent {runner.agent.name} did not produce a final response."

    try:
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response_text = event.content.parts[0].text
                elif event.actions and event.actions.escalate:
                    final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
                break
    except Exception as e:
        final_response_text = f"Error during agent execution for {agent_obj.name}: {e}"
        print(f"    <<< {final_response_text}")
        return final_response_text
    
    print(f"    <<< Response from {agent_obj.name} (first 100 chars): '{final_response_text[:100]}{'...' if len(final_response_text) > 100 else ''}'")
    return final_response_text

async def run_test_flow():
    """Allows user to select a flow, an endpoint, provide initial query, and run it."""
    print("Available predefined flows:")
    flow_names = list(predefined_flows.keys())
    for i, name in enumerate(flow_names):
        print(f"  {i + 1}. {name.replace('_', ' ').title()} (Agents: {', '.join(predefined_flows[name])})")

    # Select flow
    chosen_flow_key = None
    while True:
        try:
            flow_choice_input = input("\nSelect a flow to run (enter number): ")
            flow_index = int(flow_choice_input) - 1
            if 0 <= flow_index < len(flow_names):
                chosen_flow_key = flow_names[flow_index]
                break
            else:
                print("Invalid flow number.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    selected_flow_agents = predefined_flows[chosen_flow_key]
    print(f"\nSelected Flow: {chosen_flow_key.replace('_', ' ').title()}")
    print("Agents in this flow:")
    for i, agent_name in enumerate(selected_flow_agents):
        print(f"  {i + 1}. {agent_name}")

    # Select endpoint agent
    chosen_endpoint_index = len(selected_flow_agents) - 1 # Default to last agent
    if len(selected_flow_agents) > 1: # Only ask if more than one agent
        while True:
            try:
                endpoint_choice_input = input(f"Run up to which agent in the flow? (enter number, 1 to {len(selected_flow_agents)}, default: {len(selected_flow_agents)}): ")
                if not endpoint_choice_input: # User presses enter for default
                    break 
                endpoint_index_input = int(endpoint_choice_input) - 1
                if 0 <= endpoint_index_input < len(selected_flow_agents):
                    chosen_endpoint_index = endpoint_index_input
                    break
                else:
                    print(f"Invalid agent number. Must be between 1 and {len(selected_flow_agents)}.")
            except ValueError:
                print("Invalid input. Please enter a number or press Enter for default.")
    
    agents_to_run = selected_flow_agents[:chosen_endpoint_index + 1]
    print(f"\nWill run the following agents in sequence: {', '.join(agents_to_run)}")

    # Initial query
    current_query = input("\nEnter the initial query for the first agent ({agents_to_run[0]}): ")
    print("--- Starting Flow Execution ---")

    # Execute flow
    for agent_name_in_flow in agents_to_run:
        agent_object = available_agents.get(agent_name_in_flow)
        if not agent_object:
            print(f"\nError: Agent '{agent_name_in_flow}' not found in available_agents. Skipping.")
            current_query = f"Error: Agent '{agent_name_in_flow}' not found." # So next agent gets an error message
            continue

        # Pass the output of the previous agent (or initial query) to the current one
        next_input = await call_agent_in_flow(
            agent_obj=agent_object,
            query=current_query,
            user_id=USER_ID,
            app_name=APP_NAME,
            session_service_instance=session_service,
            session_id_counter_ref=SESSION_ID_COUNTER
        )
        current_query = next_input # Output of current becomes input for next

        if "Error:" in current_query or "Agent escalated:" in current_query :
            print(f"--- Flow interrupted due to error from {agent_name_in_flow} ---")
            break
            
    print("\n--- Flow Execution Finished ---")
    print(f"Final output after {agents_to_run[-1]}:\n{current_query}")

if __name__ == "__main__":
    try:
        asyncio.run(run_test_flow())
    except KeyboardInterrupt:
        print("\nExecution cancelled by user.")
    except Exception as e:
        print(f"An unexpected error occurred at the top level: {e}") 