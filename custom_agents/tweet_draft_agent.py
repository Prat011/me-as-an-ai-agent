from google.adk import Agent
from custom_tools.tools import twitter_tools, web_tools

tweet_draft_agent = Agent(
    name='Tweet_Draft_Agent',
    instruction='Draft a tweet to promote a video, given the path to the video file.',
    description='Drafts a tweet based on a given video path to promote it.',
    tools=twitter_tools + web_tools,
    model='gemini-2.0-flash'
) 