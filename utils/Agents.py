# Importing Necessary Libraries
from agno.agent import Agent
from agno.team.team import Team
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.models.google import Gemini
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
from utils.Prompts import IntroInstructions, NarrativeInstructions, QuizInstructions, TeamInstructions 


# Loading Env Variables
load_dotenv()
os.environ.get("GOOGLE_API_KEY")

# Setting Up Memory and Clearing it (All Sessions are Standalone)
MemoryDB = SqliteMemoryDb(table_name = "memory", db_file = "tmp/memory.db")
memory = Memory(db = MemoryDB)

# Check if there Are Memories before Clearing or Will Throw an Error
ExistingMemory = memory.get_user_memories()  
if ExistingMemory:
    memory.clear()

# Defining JSON Response Schema for the Quiz Response
class PythonChallenge(BaseModel):
    Challenge: str = Field(
        ..., description = "Given the Narrative Context the Appropriate Python Coding Challenge for the Game."
    )

# Creating the Intro Agent to Set Up the Story 
IntroAgent = Agent(
    name = "Introductory Agent",
    role = "",
    model = Gemini(id = "gemini-2.0-flash", temperature = 2),
    instructions = IntroInstructions,
    markdown = True,
    add_history_to_messages = True,
    num_history_responses = 3,
    memory = memory,
    enable_user_memories = True
)

# Creating the Narrative Agent to Drive the Narrative
NarrativeAgent = Agent(
    name = "Narrative Agent",
    role = "Given the Story, it Keeps the Storytelling Going, Aligned with the Narrative and the Challenges Given to the User.",
    model = Gemini(id = "gemini-2.0-flash"),
    instructions = NarrativeInstructions,
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
    instructions = QuizInstructions,
    markdown = True,
    add_history_to_messages = True,
    num_history_responses = 3,
    memory = memory,
    enable_user_memories=True,
    response_model = PythonChallenge
)

# Creating the Multi-Agent System
DMs = Team(
    name = "Dungeon Masters Team",
    mode = "route",
    model = Gemini(id = "gemini-2.0-flash"),
    enable_team_history = True,
    members = [IntroAgent, NarrativeAgent, QuizAgent],
    markdown = True,
    share_member_interactions = True,
    instructions = TeamInstructions
)