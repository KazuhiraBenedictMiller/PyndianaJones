# Importing Necessary Libraries
from agno.agent import Agent
from agno.team.team import Team
from agno.memory.v2.memory import Memory
from agno.models.google import Gemini
from pydantic import BaseModel, Field
from typing import List
import os
from dotenv import load_dotenv
from utils.Prompts import IntroInstructions, NarrativeInstructions, QuizInstructions, MemoryInstructions, TeamInstructions 

# Defining JSON Response Schema for the Quiz Response
class PythonChallenge(BaseModel):
    NarrativeContext: str = Field(
        ..., description = "The Narrative Context that Lead to the Challenge."
    )

    PythonCodingChallenge: str = Field(
        ..., description = "The Appropriate Python Coding Challenge Given the Narrative Context."
    )

# Defining the JSON Response Schema for the Memories
class Memories(BaseModel):
    Memories: List[str] = Field(
        ..., description = "The List of Memories given the Narrative Context."
    )

# Function to Initialize the Team of Agents
def InitializeAgents(memory: Memory) -> Team:
    # Clearing the Memory
    memory.clear()

    # Creating the Intro Agent to Set Up the Story 
    IntroAgent = Agent(
        name = "Introductory Agent",
        role = "Setting Up the Narrative for the Story",
        user_id = "PyIndy",
        model = Gemini(id = "gemini-2.0-flash", temperature = 2),
        instructions = IntroInstructions,
        markdown = True,
        # add_history_to_messages = True,
        # num_history_responses = 3,
        memory = memory,
        # enable_user_memories = True
    )

    # Creating the Narrative Agent to Drive the Narrative
    NarrativeAgent = Agent(
        name = "Narrative Agent",
        role = "Given the Story, it Keeps the Storytelling Going, Aligned with the Narrative and the Challenges Given to the User.",
        user_id = "PyIndy",
        model = Gemini(id = "gemini-2.0-flash"),
        instructions = NarrativeInstructions,
        markdown = True,
        add_history_to_messages = True,
        num_history_responses = 5,
        memory = memory,
        # enable_user_memories = True
    )

    # Creating the Agent to Actually Create the Challenges
    QuizAgent = Agent(
        name = "Quiz Agent",
        role = "Given the Narrative, it Generates Python Coding Challenges for the User in a Narrative Way.",
        user_id = "PyIndy",
        model = Gemini(id = "gemini-2.0-flash"),
        instructions = QuizInstructions,
        markdown = True,
        add_history_to_messages = True,
        num_history_responses = 5,
        memory = memory,
        # enable_user_memories = True,
        response_model = PythonChallenge
    )

    # For Some Reason Agentic Generation of Memories Doesn't Work for Narrative Type of Applications.
    # Also, I want more Granular Control Over the Memories.
    MemoryAgent =  Agent(
        name = "Memory Agent",
        role = "Given the Narrative, the Challenges, and the Overall Context, it Generates Contextual Memories that are Key Facts for the Narrative Story.",
        user_id = "PyIndy",
        model = Gemini(id = "gemini-2.0-flash"),
        instructions = MemoryInstructions,
        markdown = True,
        add_history_to_messages = True,
        num_history_responses = 5,
        memory = memory,    
        # enable_user_memories = True,
        response_model = Memories
    )

    # Creating the Multi-Agent/SubTeam System
    DungeonMaster = Team(
        name = "Dungeon Masters Team",
        mode = "route",
        model = Gemini(id = "gemini-2.0-flash"),
        user_id = "PyIndy",
        enable_team_history = True,
        members = [IntroAgent, NarrativeAgent, QuizAgent],
        markdown = True,
        share_member_interactions = True,
        instructions = TeamInstructions,
        memory = memory,
        read_team_history = True,
        enable_agentic_context = True, 
        enable_user_memories = True
    )

    return MemoryAgent, DungeonMaster 