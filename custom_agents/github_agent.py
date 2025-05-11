from google.adk import Agent
from custom_tools.tools import github_tools, web_tools

github_agent = Agent(
    name='Github_Agent',
    instruction='Create commits with given messages and then create pull requests for the changes.',
    description='Handles git commits and pull request creation.',
    tools=github_tools + web_tools,
    model='gemini-2.0-flash'
)
