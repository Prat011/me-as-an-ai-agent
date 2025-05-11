from langchain_openai import ChatOpenAI
from browser_use import Agent
from dotenv import load_dotenv
load_dotenv()

import asyncio

llm = ChatOpenAI(model="gpt-4o")

async def main():
    agent = Agent(
        task="Go to x.com, login with mastmelon82 and password is broiamsickofthis, scroll 100 tweets and list ones related to ai",
        llm=llm,
    )
    result = await agent.run()
    print(result)

asyncio.run(main())