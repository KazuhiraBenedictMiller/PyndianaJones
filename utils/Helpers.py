# Importing Necessary Libraries
from agno.agent import Agent, RunResponse
from agno.team.team import Team
from agno.agent import RunResponse
from agno.memory.v2.memory import UserMemory
from typing import Union
import re

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
        '"': '"SPEECH"',
        '_': '_DEBUG_'
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

def GeneratePushMemories(MemAgent: Agent, DMAgent: Team, Res: str):
    # Generating Memories
    Mems: RunResponse = MemAgent.run(Res, user_id = "PyIndy")

    # Since Memories are In Cronological Order - First to Last, we need to Reverse Them
    ReversedMems = Mems.content.Memories[::-1]

    # Adding Memories to the Dungeon Master
    for m in ReversedMems:
        DMAgent.memory.add_user_memory(UserMemory(m), user_id = "PyIndy")
