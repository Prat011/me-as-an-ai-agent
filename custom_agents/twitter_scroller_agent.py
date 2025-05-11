from google.adk import Agent
from custom_tools.tools import twitter_scroll_tools, web_tools

twitter_scroller_agent = Agent(
    name='Twitter_Scroller_Agent',
    description='Scroll through recent tweets, identify the top 10 AI-related tweets based on likes and views, and compile a list.',
    instruction='Scroll through 1000/2000 tweets. Makes a list of top 10 tweets related to AI Agents based on likes and views but only related to ai. Fetch the user s id then fetch the home timeline and list timeline of id: 1868699620718919863, while fetching home timeline just pass the id parameter, don t pass the tweet fields parameter.',
    tools=twitter_scroll_tools,
    model='gemini-2.5-flash-preview-04-17'
) 