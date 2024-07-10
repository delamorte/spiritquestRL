from game_states import NpcStates
from ui.menus import MenuData


class Npc:
    def __init__(self, name, quest=None, home=None, action=None):
        self.owner = None
        self.name = name
        self.quest = quest
        self.home = home
        self.action = action
        self.prev_state = None
        if quest:
            self.state = NpcStates.QUEST_INITIATED
        else:
            self.state = NpcStates.IDLE

    def interaction(self, menus):
        params = self.owner.dialogue
        dialogue_data = MenuData(name="dialogue", params=params)
        menus.create_or_show_menu(dialogue_data)
        return

    def set_state(self, state):
        self.prev_state = self.state
        self.state = NpcStates(state)
