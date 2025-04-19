# Importing Necessary Libraries
from agno.agent import RunResponse
from utils.Agents import DMs
from rich.console import Console
from rich.markdown import Markdown
from rich.box import HEAVY
from rich.panel import Panel
from rich.prompt import Prompt
import os
from dotenv import load_dotenv
import subprocess

# Loading Env Variables
load_dotenv()
os.environ.get("GOOGLE_API_KEY")

# Instantiating Console Object
console = Console()

# Defining Welcome Message
Intro = Markdown("""
### Welcome to Pyndiana Jones!

This is a Roguelike, Text Based, and AI-Generated Game where You will Play as **Indiana Jones** - or _Indy_ - to Solve Enigmas in the form of Python Coding Challenges while You Progress Throughout the Narrative.

There is No Right or Wrong Answer, your Successes and Mistakes will Shape the Narrative!

**Here is a List of Useful Commands (Inputs):**

- `quit`: Quit the game instantly
- `!action`: Make Indy Perform an Action
- `<thought>`: Make Indy Think about Something
- `"speech"`: Make Indy Say Something
""")

# Displaying Welcome Message
WelcomePanel = Panel(Intro, box=HEAVY, border_style = "orange4", padding=(1, 1))
console.print(WelcomePanel)

console.print(" ")

# Asking the User for Its Favourite Editor
Editor = Prompt.ask("Before we Begin Our Adventure, what is your Favourite Text Editor? (nano, vim)")

while Editor.lower() not in ["nano", "vim"]:
    console.print(" ")
    Editor = Prompt.ask("Only 'nano' and 'vim' are Supported for Editing Code Files, Now, what is your Favourite Text Editor?")

# Displaying Begin Message
console.print(" ")
console.print("Great, Let's Start a New Adventure")
console.print(" ")

# Thick Line for Readability
console.rule(style = "orange4", characters = "━")  
console.print(" ")

# Beginning Adventure
Response: RunResponse = DMs.run("Let's Start a New Adventure")
console.print(Markdown(Response.content))

# Main Game Loop
while True:
    # Asking the User what Indy will !DO/<THINK>/"SAY"
    console.print(" ")
    AskUser = Prompt.ask('What Will [italic orange4]Indy[/italic orange4] [gold1]!DO[/gold1]/[chartreuse3]<THINK>[/chartreuse3]/[steel_blue1]"SAY"[/steel_blue1]')

    # quit for Quitting the Game
    if AskUser.lower() == "quit":
        GoodbyePanel = Panel(Markdown("### Thanks for Playing Pyndiana Jones!"), box = HEAVY, border_style = "orange4", padding = (1, 1))
        console.print(GoodbyePanel)
        break

    # For Every Other Input
    else:
        # Querying the Team of Agents
        console.print(" ")
        Response: RunResponse = DMs.run(AskUser)
                
        try:
            # If the Answer is Printable
            console.print(Markdown(Response.content))
        except TypeError:
            # If the Answer is Actually an Object (Code)
            # Mkdir code Folder if it doesn't Exist
            if not os.path.exists("./code"):
                try:
                    os.mkdir("./code")
                except:
                    print("An Error Occurred Whilist Trying to Create the code Folder")

            # Get the Code to Prepopulate the Editor
            ChallengeCode = Response.content.Challenge

            # Writing Code to File
            with open("./code/Solution.py", "w") as f:
                f.write(ChallengeCode)

            # Opening the File with the Terminal Text Editor (Will Stop Execution of the Program)
            subprocess.call([Editor, "--wait", "./code/Solution.py"])

            # Readding the Content After Editing
            with open("./code/Solution.py", 'r') as f:
                SolutionCode = f.read()

            # Sending the Solution to the Team of Agents and Querying Again
            console.print(" ")
            Response: RunResponse = DMs.run("Here's the Solution:\n" + SolutionCode)
            console.print(Markdown(Response.content))