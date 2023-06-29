from data import json_data


class Dialogue:
    def __init__(self, actor):
        self.owner = None
        self.actor = actor
        self.dialogue_json = json_data.data.dialogue[actor]
        self.prompt_state = "100"
