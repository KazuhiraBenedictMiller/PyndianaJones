# Importing Necessary Libraries
from agno.agent import RunResponse
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory, UserMemory
from utils.Agents import InitializeAgents
from rich.console import Console
from rich.markdown import Markdown
from rich.box import HEAVY
from rich.panel import Panel
from rich.prompt import Prompt
import os
from dotenv import load_dotenv
import subprocess
import re
from time import sleep

# Function to Format the Input Prompt
def FormatInputPrompt(InputPrompt: str) -> str:
    """
    Finds every !…!, <…>, or "…" Segments in the InputText, 
    Then Normalizes it to GENERIC_TAG + blank line + inner text, ...
    Lastly Joins them with Blank Lines.
    """

    # Compiling the Pattern to Handle !…!, <…>, and "…"
    DoThinkSayPattern = re.compile(
        r'!(?P<i1>.*?)!'   # Action Wrapper
        r'|<(?P<i2>.*?)>'  # Thought Wrapper
        r'|"(?P<i3>.*?)"'  # Speech Wrapper
    )

    # Mapping Each Delimiter to the Normalized TAG
    TagMap = {
        '!': '!ACTION!',
        '<': '<THINKING>',
        '"': '"SPEECH"'
    }

    Outputs = []
    for rgx in DoThinkSayPattern.finditer(InputPrompt):
        # Finding Which Group Matched
        if rgx.group('i1') is not None:
            InnerText = rgx.group('i1').strip()
            Delimiter = '!'
        elif rgx.group('i2') is not None:
            InnerText = rgx.group('i2').strip()
            Delimiter = '<'
        else:
            InnerText = rgx.group('i3').strip()
            Delimiter = '"'

        Normalize = TagMap[Delimiter]
        Outputs.append(f"{Normalize}\n\n{InnerText}")

    return "\n\n".join(Outputs)

# Loading Env Variables
load_dotenv()
os.environ.get("GOOGLE_API_KEY")

# Initializing Memory for the Agents
# Setting Up Memory and Clearing it (All Sessions are Standalone)
MemoryDB = SqliteMemoryDb(table_name = "memory", db_file = "tmp/memory.db")
AgentsMemory = Memory(db = MemoryDB)


# Check if there Are Memories before Clearing or Will Throw an Error
ExistingMemory = AgentsMemory.get_user_memories()  
if ExistingMemory:
    MemoryDB.clear()
    AgentsMemory.clear()

# Instantiating Console Object
console = Console()

# Defining Welcome Message
Intro = Markdown("""
### Welcome to Pyndiana Jones!

This is a Roguelike, Text Based, and AI-Generated Game where You will Play as **Indiana Jones** - or _Indy_ - to Solve Enigmas in the form of Python Coding Challenges while You Progress Throughout the Narrative.

There is No Right or Wrong Answer, your Successes and Mistakes will Shape the Narrative!

**Here is a List of Useful Commands (Inputs):**

- `quit`: Quit the game instantly
- `!Action!`: Make Indy Perform an Action
- `<Thought>`: Make Indy Think or Reflect about Something
- `"Speech"`: Make Indy Say Something

**NOTE:** Commands can be Queried Sequentially, for Example:

_<Hmmm, Maybe I can Find an Entrance to that Cave> !I Look Around for an Entrance!_
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

# Defining the Dungeon Master and Memory Agent
MemoryAgent, DungeonMaster = InitializeAgents(AgentsMemory)

# Reduntant, but Just in Case
DungeonMaster.memory.clear()
MemoryAgent.memory.clear()

# Beginning Adventure
Response: RunResponse = DungeonMaster.run("Let's Start a New Adventure", user_id = "PyIndy")
console.print(Markdown(Response.content))

# Generating Memories
Mems: RunResponse = MemoryAgent.run(Response.content, user_id = "PyIndy")

# Adding Memories
# Adding Memories to the Dungeon Master
for m in Mems.content.Memories:
    DungeonMaster.memory.add_user_memory(UserMemory(m), user_id = "PyIndy")

# Main Game Loop
while True:
    
    # Debugging Memories
    console.rule(style = "orange4", characters = "━")  
    console.print("")

    memories = DungeonMaster.memory.get_user_memories("PyIndy")

    print("Indy's memories:")
    for i, m in enumerate(memories):
        print(f"{i}: {m.memory}")

    console.print("")   
    console.rule(style = "orange4", characters = "━")  
    console.print("")

    # Asking the User what Indy will !DO/<THINK>/"SAY"
    console.print(" ")
    AskUser = Prompt.ask('What Will [italic bold orange4]Indy[/italic bold orange4] [bold gold1]!DO![/bold gold1]/[bold chartreuse3]<THINK>[/bold chartreuse3]/[bold steel_blue1]"SAY"[/bold steel_blue1]')

    # quit for Quitting the Game
    if AskUser.lower() == "quit":
        GoodbyePanel = Panel(Markdown("### Thanks for Playing Pyndiana Jones!"), box = HEAVY, border_style = "orange4", padding = (1, 1))
        console.print(GoodbyePanel)
        DungeonMaster.memory.clear()
        MemoryAgent.memory.clear()
        break

    # For Every Other Input
    else:
        # Querying the Team of Agents
        console.print(" ")

        # Formatting the Prompt
        try: 
            FormattedPrompt = FormatInputPrompt(AskUser)   
            Response: RunResponse = DungeonMaster.run(FormattedPrompt) # , user_id = "PyIndy")
        except:
            # If It Fails, we Query Directly - Contains Typos 
            Response: RunResponse = DungeonMaster.run(AskUser) # , user_id = "PyIndy")    

        # Displaying the AI Message
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

            # Getting the Context Leading to the Challenge
            Context = Response.content.NarrativeContext

            # Get the Code to Prepopulate the Editor
            ChallengeCode = Response.content.PythonCodingChallenge

            console.print(Markdown(Context))

            # Writing Code to File
            with open("./code/Solution.py", "w") as f:
                f.write(ChallengeCode)

            # Giving User the Time to Read
            sleep (3)

            # Opening the File with the Terminal Text Editor (Will Stop Execution of the Program)
            subprocess.call([Editor, "./code/Solution.py"])

            # Readding the Content After Editing
            with open("./code/Solution.py", 'r') as f:
                SolutionCode = f.read()

            # Sending the Solution to the Team of Agents and Querying Again
            console.print(" ")
            Response: RunResponse = DungeonMaster.run("Here's the Solution:\n" + SolutionCode) # , user_id = "PyIndy")
            console.print(Markdown(Response.content))