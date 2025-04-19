import json
from textwrap import dedent
from typing import Optional
import asyncio
import typer
from agno.agent import Agent, RunResponse
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.storage.sqlite import SqliteStorage
from agno.team.team import Team
from rich.console import Console
from rich.markdown import Markdown
from rich.json import JSON
from rich.panel import Panel
from rich.prompt import Prompt
import os
from dotenv import load_dotenv
from agno.models.google import Gemini

# Loading Env Variables
load_dotenv()
os.environ.get("GOOGLE_API_KEY")


import base64
import os
from google import genai
from google.genai import types


def generate():
    client = genai.Client(api_key = os.environ.get("GOOGLE_API_KEY"))

    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""miao
"""),
            ],
        ),
        types.Content(
            role="model",
            parts=[
                types.Part.from_text(text="""Meow! 🐱
"""),
            ],
        ),
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""INSERT_INPUT_HERE"""),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        print(chunk.text, end="")

if __name__ == "__main__":
    generate()
