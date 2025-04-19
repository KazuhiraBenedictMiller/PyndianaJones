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
from rich.syntax import Syntax
import os
from dotenv import load_dotenv
from agno.models.google import Gemini
import subprocess

# Loading Env Variables
load_dotenv()
os.environ.get("GOOGLE_API_KEY")


# Setting Up Memory and Clearing it (All Sessions are Standalone)
memory_db = SqliteMemoryDb(table_name = "memory", db_file = "tmp/memory.db")
memory = Memory(db = memory_db)
memory.clear()


from pydantic import BaseModel, Field


class PythonChallenge(BaseModel):
    Challenge: str = Field(
        ..., description = "Given the Narrative Context the Appropriate Python Coding Challenge for the Game."
    )

# Creating the Intro Agent to Set Up the Story 
IntroAgent = Agent(
    name = "Introductory Agent",
    model = Gemini(id = "gemini-2.0-flash", temperature = 2),
    instructions = dedent("""\
        You are a Dungeon Master that will guide the User Through one of the Indiana Jones Adventures with a flair for storytelling! 
        Think of yourself as a Narrator.

        The Game You will Play with the User:
        - Will Have a Title for the Adventure
        - Will Start with a Date and Location, For Example: Year, City, Location
        - Will Give a Nice Introduction to the Story to Capture the Players Attention
        - Make Sure the Adventures are Historically Located Within the 1910s and 1970s.
        - Never Ask Questions to the User, waiting for them to Drive the Narrative
        - Make sure all the Adventures are not the Official Indiana Jones one, but some made up, where you can Leverage Creativity.
        - Will Always Be Presented in 2nd Person.
        - Make Sure you Are only Returning The Answer Without any Intros or Outros\
    """),
    markdown = True,
    add_history_to_messages = True,
    num_history_responses = 3,
    memory = memory,
    enable_user_memories = True
)

NarrativeAgent = Agent(
    name = "Narrative Agent",
    role = "Given the Story, it Keeps the Storytelling Going, Aligned with the Narrative and the Challenges Given to the User.",
    model = Gemini(id = "gemini-2.0-flash"),
    instructions = dedent("""\
        You are a Dungeon Master that will guide the User Through one of the Indiana Jones Adventures with a flair for storytelling! 
        Think of yourself as a Narrator.

        The Game You will Play with the User:
        - Will Always Be Presented in 2nd Person.
        - You will be Tasked to Drive the Main Narrative for the Story, given the Context.
        - Never Ask Questions to the User, waiting for them to Drive the Narrative
        - Make sure all the Adventures are not the Official Indiana Jones one, but some made up, where you can Leverage Creativity.
        - Make Sure you Are only Returning The Answer Without any Intros or Outros\
    """),
    markdown = True,
    add_history_to_messages = True,
    num_history_responses = 3,
    memory = memory,
    enable_user_memories = True
)

# Creating the Agent to Actually Create the Challenges
QuizAgent = Agent(
    name = "Quiz Agent",
    role = "Given the Narrative, it Generates Python Challenges for the User in a Narrative Way.",
    model = Gemini(id = "gemini-2.0-flash"),
    instructions = dedent("""\
        You are an Expert Python Teacher, and you are Passionate About Employments of Gamification in Learning Experiences.
        You are Teaming up with a Narrator for Building a Python Based Textual Game Resembling Indiana Jones, where Mysteries, Secrets and Enigma are to be Solved with Python Code.
        Given a Narrative, Your Task is to Decide Whether or not is is appropriate to Place a Challenge for the User.
        Specifically, You will have to create the Challenge that will be Solved with Python, where the User will Have to Pass the Challenge to Progress throughout the Story.

        The Challenges You Will Create:
        - Given the Context and the Storyline, You will Propose an Appropriate Coding Challenge.
        - Will be Incomplete Python Code, where the User will have to complete that Code in a Delimited Code Section, For Instance:
            # Python Code
            # Description of the Challenge
            # HINTS: Hints for the Challenge

            This is where you will place the Python code that the User will Have to Complete to Solve the Challenge

            ### START OF USER CODE ###

                This Should be Left Empty, so the User can Practice its Python Skills by Completing the Code in the Previous Section

            ### END OF USER CODE ###

        - The Code should Always Print or Return an Answer to Check if the Player Successfully Completed The Challenge.
        - The Solutions Given by the User can be in 2 Different Formats:
            1) The Complete Python Code
            2) Only the Part that should go Within the ### USER CODE ### Section with an Explanation.
        
        - You will Check if the Provided Python Code is Accurate, then, Given the Correctness of the Code You will Drive the Narrative Following it.
            - Totally Wrong Code: Indiana Jones didn't Solve the Enigma, You Explain the Errors made by the User in a Storytelling Fashion and Drift or Pivot the Narrative in a Different Direction.
            - Partially Correct Output: You give a Narrative Styled Feedback to the Player, but Slightly Drift the Narrative (Challenge Completed but not in the Best Way).
            - Totally Correct Output: The Challenge was Completed Successfully, you Explain in a Narrative Format why the Challenge was Successful, and Move on with the Narrative. 

        - Never Ask Questions to the User, waiting for them to Drive the Narrative.
        - Make sure all the Adventures are not the Official Indiana Jones one, but some made up.
        - Make Sure you Are only Returning The Challenge Without any Intros or Outros.
        - Make Sure the Challenges are Progressively Harder to Solve, with the First one Being the Easiest, and Subsequent Ones Increasigly Harder.\
    """),
    markdown = True,
    add_history_to_messages = True,
    num_history_responses = 3,
    memory = memory,
    enable_user_memories=True,
    response_model = PythonChallenge

)

DMs = Team(
    name = "Dungeon Masters Team",
    mode = "route",
    model = Gemini(id = "gemini-2.0-flash"),
    enable_team_history = True,
    members = [IntroAgent, NarrativeAgent, QuizAgent],
    markdown = True,
    share_member_interactions = True,
    instructions=[
        "You are the Lead Dungeon Master for a Text Based Game, Inspired by Indiana Jones, where the User needs to Solve Challenges with Python Code to Progres Throughout the Narrative."
        "Carefully analyze each user message and determine if it's Time to Start the Story, it's Time for More Narrative, or if it's time for a Coding Challenge in Python.", 
        "For Starting the Story, always route to the IntroAgent, who will set up the Narrative. Once Invoked, it will Never be Invoked Again.",
        "For Advancing the Story, immediately route to the NarrativeAgent.",
        "If you think it's Time for a Python Coding Challenge, route to the QuizAgent.",
        "After receiving a response from the appropriate agent, simply redirect that information back to the Player while keeping the Narrative Tone.",
        "Ensure a seamless experience for the user by maintaining context throughout the Narrative.",
        "Ensure that the Narrative Follows a Logic and a Story Telling."
        "Make Sure you Are only Returning The Answer Without any Intros or Outros"
    ],
)

Response: RunResponse = DMs.run("Let's Start a New Adventure")
#print(Response.content)
console = Console()
console.print(Markdown(Response.content))

while True:
    console.print(" ")
    AskUser = Prompt.ask("What Will Indy DO/THINK/SAY?", default = "")

    if AskUser.lower() == "quit":
        break

    else:
        console.print(" ")
        Response2: RunResponse = DMs.run(AskUser)
                
        try:
            console.print(Markdown(Response2.content))
        except TypeError:
            if not os.path.exists("./code"):
                os.mkdir("./code")

            # console.print(Syntax(Response2.content.Challenge, "python", theme = "dracula", line_numbers = True))
            import os

            # Define the code to be pre-populated in the editor
            code = Response2.content.Challenge

            with open("./code/Solution.py", "w") as f:
                f.write(Response2.content.Challenge)

            # Open the temporary file with nano
            subprocess.call(['nano', "./code/Solution.py"])

            # Read the contents after editing
            with open("./code/Solution.py", 'r') as tmp_file:
                edited_content = tmp_file.read()

            # Use the edited content as needed
            #console.print(edited_content)

            console.print(" ")
            Response2: RunResponse = DMs.run("Here's the Solution:\n" + edited_content)
            console.print(Markdown(Response2.content))




            