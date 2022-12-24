from enum import Enum

from ui.menus import MenuData


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

    def interaction(self, menus,):
        params = self.owner.dialogue
        dialogue_data = MenuData(name="dialogue", params=params)
        menus.create_or_show_menu(dialogue_data)
        return



