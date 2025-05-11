from google.adk import Agent
from custom_tools.tools import slack_tools, web_tools

video_recording_agent = Agent(
    name='Video_Recording_Agent',
    instruction='Ping on Slack to remind the user that they have to record videos.',
    description='Pings on Slack to notify the user about pending video recording tasks.',
    tools=slack_tools + web_tools,
    model='gemini-2.0-flash'
)
