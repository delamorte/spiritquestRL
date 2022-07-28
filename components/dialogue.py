from data import json_data


class Dialogue:
    def __init__(self, actor):
        self.owner = None
        self.actor = actor
        self.dialog_tree = json_data.data.dialogue[actor]["dialogue"]
