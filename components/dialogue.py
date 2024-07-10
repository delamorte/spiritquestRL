from components.npc import NpcStates
from data import json_data


class Dialogue:
    def __init__(self, name, npc):
        self.owner = None
        self.actor = name
        self.npc = npc
        self.dialogue_json = json_data.data.dialogue[self.actor]
        if self.npc.state == NpcStates.IDLE:
            self.current_choice = "100"
        else:
            self.current_choice = None
