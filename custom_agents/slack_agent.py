from google.adk import Agent
from custom_tools.tools import slack_tools, web_tools

slack_agent = Agent(
    name='Slack_Agent',
    instruction='Notify via Slack when a new agent build is complete, providing a PR link and a reminder to record a video.',
    description="Pings me on slack telling me the agent is ready and I've to record the video and sends me the pr link.",
    tools=slack_tools + web_tools,
    model='gemini-2.0-flash'
)