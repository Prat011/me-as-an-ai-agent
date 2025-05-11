from google.adk import Agent
from custom_tools.tools import slack_tools, twitter_tools, web_tools

tweet_poster_agent = Agent(
    name='Tweet_Poster_Agent',
    instruction='Post a tweet by pinging the Typefully link on Slack.',
    description='Slack agent pings the typefully link to post a tweet.',
    tools=slack_tools + twitter_tools + web_tools,
    model='gemini-2.0-flash'
)
