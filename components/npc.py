from enum import Enum


class NpcStates(Enum):
    IDLE = 1
    QUEST_INITIATED = 2
    QUEST_COMPLETED = 3
    QUEST_FAILED = 4
    HOSTILE = 5


class Npc:
    def __init__(self, name):
        self.owner = None
        self.name = name


