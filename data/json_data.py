import json

data = None


def fetch_data(path):
    with open(path) as file:
        d = json.load(file)
    return d


class JsonData:
    def __init__(self, root="data/"):
        self.root = root
        self.fighters = fetch_data(self.root + "fighters.json")
        self.abilities = fetch_data(self.root + "abilities.json")
        self.status_effects = fetch_data(self.root + "status_effects.json")
        self.remarks = fetch_data(self.root + "remarks.json")
        self.tiles = fetch_data(self.root + "tiles.json")
        self.dialogue = fetch_data(self.root + "dialogue.json")
