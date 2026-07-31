from llm import Agent, prompt_toolkit_sink
from config import load_config

from openai import AsyncClient
from loguru import logger
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

import aiofiles
import asyncio
import random

logger.remove()

logger.add(
    prompt_toolkit_sink,
    format="<green>{time:HH:mm:ss}</green> | <level>{level:7}</level> | <blue>{message}</blue>\r",
    colorize=True
)

session = PromptSession()

NUM_AGENT = 5

async def mod():
    """Fucking Arch Linux stdin wrapper"""
    moderator = await session.prompt_async("Moderator message: ")
    logger.info(f"MOD:\n{moderator}")
    return "moderator", {
        "role": "user",
        "content": f"MOD:\n{moderator}"
    }

async def delayed_agent_respond(agent, pool, delay=2.5):
    await asyncio.sleep(delay)
    return await agent.respond(pool.copy())

async def main():
    conf = load_config()
    client = AsyncClient(
        api_key=conf["api_key"],
        base_url=conf["base_url"],
    )
    model = conf["model"]

    async with aiofiles.open("system_prompt.txt", "r") as file:
        system_prompt = await file.read()

    agents = {
        f"agent_{i}": Agent(client, model, system_prompt, f"agent_{i}")
        for i in range(NUM_AGENT)
    }

    pool = [
        {
            "role": "user",
            "content": "MOD: Welcome to the discussion. Feel free to discuss ANYTHING you can think of."
        }
    ]

    tasks = set()

    result = await random.choice(list(agents.values())).respond(pool)

    pool.append(result[1])

    # Start agent tasks
    for agent in agents.values():
        tasks.add(asyncio.create_task(agent.respond(pool.copy())))

    # Start moderator input task
    tasks.add(asyncio.create_task(mod()))

    with patch_stdout():
        while tasks:
            done, pending = await asyncio.wait(
                tasks,
                return_when=asyncio.FIRST_COMPLETED
            )

            tasks = set(pending)

            # Process ALL completed tasks in this cycle
            for completed_task in done:
                result = await completed_task

                # Append response to shared pool
                pool.append(result[1])

                if result[0] == "moderator":
                    # Immediately prompt for the next moderator message
                    tasks.add(asyncio.create_task(mod()))
                else:
                    # Re-queue agent response non-blockingly with delay
                    agent = agents[result[0]]
                    tasks.add(asyncio.create_task(delayed_agent_respond(agent, pool)))

asyncio.run(main())
