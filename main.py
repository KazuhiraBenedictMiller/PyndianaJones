
'''
from rich.console import Console
from rich.panel import Panel

import os
from dotenv import load_dotenv

from agno.agent import Agent, RunResponse
from agno.models.google import Gemini

from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.storage.sqlite import SqliteStorage


# Initializing Console
console = Console()

# Space for Readability
console.print("")

# Defining Style for Main Entry and Displaying Welcome
style = "bold white on orange4"
console.print(Panel("Welcome to Pyndiana Jones.\nYou Are an Explorer in the 1930s and You will Have to Solve Puzzles and Enigmas by Coding in Python.", title = "Pyndiana Jones"),  style = style, justify = "center")

# Space for Readability
console.print("")

# Asking the User if it Wants to Play a New Game

# If the Sessions Directory does Not Exists, Create it
if not os.path.exists("./Sessions"):
    os.mkdir("./Sessions")

answer = False

while answer not in ["yes", "no", "y", "n"]: 
    answer = console.input("[bold white]:smiley: Would You Like to Start a New Game? (Yes/No) [/]")

    if answer.lower() not in ["yes", "no", "y", "n"]: 
        console.print("[bold white]Only Yes, No, Y, N Are Accepted as Answers[/]")
        console.print("")

console.print("")

# Initialize storage for both agent sessions and memories
agent_storage = SqliteStorage(table_name="agent_memories", db_file="Sessions/agents.db")


load_dotenv()
os.environ.get("GOOGLE_API_KEY")


import json
from textwrap import dedent
from typing import Optional

import typer
from agno.agent import Agent


from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.storage.sqlite import SqliteStorage


from rich.console import Console
from rich.json import JSON
from rich.panel import Panel
from rich.prompt import Prompt

agent = Agent(model=Gemini(id = "gemini-2.0-flash-exp"), markdown = True, add_history_to_messages = True, num_history_responses = 3,
#Configure memory system with SQLite storage
        memory=Memory(
            db=SqliteMemoryDb(
                table_name="agent_memory",
                db_file="Sessions/agent_memory.db",
            ),
        ),
        enable_user_memories=True,
        enable_session_summaries=True,
        storage=agent_storage,
        # Enhanced system prompt for better personality and memory usage
        description = """\
        You are a helpful and friendly AI assistant with excellent memory.
        - Remember important details about users and reference them naturally
        - Maintain a warm, positive tone while being precise and helpful
        - When appropriate, refer back to previous conversations and memories
        - Always be truthful about what you remember or don't remember"""
    )

run: RunResponse = agent.run("Tell me a Joke")
console.print(run.content)


# Print user memories
for user_id in list(agent.memory.memories.keys()):
    console.print(
        Panel(
            JSON(
                json.dumps(
                [
                    user_memory.to_dict()
                    for user_memory in agent.memory.get_user_memories(user_id=user_id)
                ],
                    indent=4,
                ),
            ),
            title=f"Memories for user_id: {user_id}",
            expand=True,
        )
    )
# Print session summary
for user_id in list(agent.memory.summaries.keys()):
    console.print(
        Panel(
            JSON(
                json.dumps(
                    [
                        summary.to_dict()
                        for summary in agent.memory.get_session_summaries(user_id=user_id)
                    ],
                    indent=4,
                ),
            ),
            title=f"Summary for session_id: {agent.session_id}",
            expand=True,
        )
    )


# console.input("What is [i]your[/i] [bold red]name[/]? :smiley: ")

'''

import json
from textwrap import dedent
from typing import Optional

import typer
from agno.agent import Agent
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.storage.sqlite import SqliteStorage
from rich.console import Console
from rich.json import JSON
from rich.panel import Panel
from rich.prompt import Prompt
import os
from dotenv import load_dotenv
from agno.models.google import Gemini


load_dotenv()
os.environ.get("GOOGLE_API_KEY")

# Initialize storage for both agent sessions and memories
agent_storage = SqliteStorage(table_name="agent_memories", db_file="tmp/agents.db")

agent = Agent(
    model=Gemini(id = "gemini-2.0-flash-exp"),
    user_id=user,
    session_id=session_id,
    # Configure memory system with SQLite storage
    memory=Memory(
        db=SqliteMemoryDb(
            table_name="agent_memory",
            db_file="tmp/agent_memory.db",
        ),
    ),
    enable_user_memories=True,
    enable_session_summaries=True,
    storage=agent_storage,
    add_history_to_messages=True,
    num_history_responses=3,
    # Enhanced system prompt for better personality and memory usage
    description=dedent("""\
        You are a helpful and friendly AI assistant with excellent memory.
        - Remember important details about users and reference them naturally
        - Maintain a warm, positive tone while being precise and helpful
        - When appropriate, refer back to previous conversations and memories
        - Always be truthful about what you remember or don't remember"""),
    )

if session_id is None:
    session_id = agent.session_id
    if session_id is not None:
        print(f"Started Session: {session_id}\n")
    else:
        print("Started Session\n")
else:
    print(f"Continuing Session: {session_id}\n")


console = Console()

messages = []
session_id = agent.session_id
session_run = agent.memory.runs[session_id][-1]
for m in session_run.messages:
    message_dict = m.to_dict()
    messages.append(message_dict)


# Print chat history
console.print(
        Panel(
            JSON(
                json.dumps(
                    messages,
                ),
                indent=4,
            ),
            title=f"Chat History for session_id: {session_run.session_id}",
            expand=True,
        )
    )

    # Print user memories
for user_id in list(agent.memory.memories.keys()):
    console.print(
            Panel(
                JSON(
                    json.dumps(
                    [
                        user_memory.to_dict()
                        for user_memory in agent.memory.get_user_memories(user_id=user_id)
                    ],
                        indent=4,
                    ),
                ),
                title=f"Memories for user_id: {user_id}",
                expand=True,
            )
        )

    # Print session summary
for user_id in list(agent.memory.summaries.keys()):
    console.print(
            Panel(
                JSON(
                    json.dumps(
                        [
                            summary.to_dict()
                            for summary in agent.memory.get_session_summaries(user_id=user_id)
                        ],
                        indent=4,
                    ),
                ),
                title=f"Summary for session_id: {agent.session_id}",
                expand=True,
            )
        )



exit_on = ["exit", "quit", "bye"]
while True:
    message = Prompt.ask(f"[bold] :sunglasses: {user} [/bold]")
    if message in exit_on:
        break

    agent.print_response(message=message, stream=True, markdown=True)
    print_agent_memory(agent)


if __name__ == "__main__":
    typer.run(main)
