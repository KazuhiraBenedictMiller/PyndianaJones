import os
from dotenv import load_dotenv

from agno.agent import Agent, RunResponse
from agno.models.google import Gemini

import asyncio
'''
# --- Load API Key ---
load_dotenv()

os.environ.get("GOOGLE_API_KEY")

agent = Agent(model=Gemini(id="gemini-2.0-flash-exp"), markdown=True,         add_history_to_messages=True,
        num_history_responses=3,)

class Conversation:
    def __init__(self) -> None:
        self.messages: list[dict] = []

    async def send(self, message: str) -> list[str]:
        self.messages.append({"role": "user", "content": message})
        run: RunResponse = agent.run(message)
        return [run.content]

    def clear(self) -> None:
        self.messages = []

async def main() -> None:
    conversation = Conversation()
    while True:
        msg = input("Type your message: ")
        results = await conversation.send(msg)
        print(results)

if __name__ == "__main__":
    asyncio.run(main())

'''

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Placeholder

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Input, Button
from textual.containers import Container, Horizontal

from textual.widget import Widget

class ChatApp(App):
    ...  # trunkated code

    async def on_button_pressed(self) -> None:
        await self.process_conversation()

    async def on_input_submitted(self) -> None:
        await self.process_conversation()

    async def process_conversation(self) -> None:
        message_input = self.query_one("#message_input", Input)
        # Don't do anything if input is empty
        if message_input.value == "":
            return
        button = self.query_one("#send_button")

        self.toggle_widgets(message_input, button)

        # Clean up the input without triggering events
        with message_input.prevent(Input.Changed):
            message_input.value = ""

    def toggle_widgets(self, *widgets: Widget) -> None:
        for w in widgets:
            w.disabled = not w.disabled

if __name__ == "__main__":
    app = ChatApp()
    app.run()

