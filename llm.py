from openai import AsyncClient
from loguru import logger
from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.patch_stdout import StdoutProxy

import asyncio

def prompt_toolkit_sink(message: str):
    print_formatted_text(ANSI(message.rstrip("\n")))

class Agent:
    def __init__(self, client: AsyncClient, model: str, system_prompt: str, id: str):
        logger.remove()
        logger.add(
            prompt_toolkit_sink,
            colorize=True
        )

        self.client = client
        self.id = id
        self.model = model
        self.system_prompt = system_prompt

    async def respond(self, input: list):
        await asyncio.sleep(2.5)
        resp = await self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": self.system_prompt,
                },
                {
                    "role": "system",
                    "content": f"""
                    You are currently {self.id}, refer to other agents using the @ tag.
                    Available system-wide tag:
                        - @all: Refer to everyone.
                        - @mod: Refer to moderator.
                    The system will add your name as prefix to your message. Do not do that yourself.
                    """,
                },
                *input,
            ],
            model=self.model,
            n=1,
        )

        content = resp.choices[0].message

        msg = {
            "role": "user",
            "content": f"{self.id}:\n{content.content}",
        }

        logger.debug(f"{self.id}:\n{content.content}")

        return self.id, msg
