import json


def fetch_data(path):
    with open(path) as file:
        data = json.load(file)
    return data


class JsonData:
    def __init__(self, root="data/"):
        self.root = root
        self.fighters = fetch_data(self.root + "fighters.json")
        self.abilities = fetch_data(self.root + "abilities.json")
