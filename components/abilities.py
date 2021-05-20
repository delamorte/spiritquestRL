from components.ability import Ability
from data import json_data


class Abilities:
    def __init__(self, name, capacity=None):
        self.name = name
        self.capacity = capacity
        self.items = []

        if name != "player":
            self.initialize_abilities()

    def initialize_abilities(self, name=None):
        if name is None:
            name = self.name
        initial_abilities = json_data.data.fighters[name]["abilities"]
        for n in initial_abilities:
            item = json_data.data.abilities[n]
            name = item["name"]
            description = item["description"]
            skill_type = item["skill_type"]
            damage = item["damage"] if "damage" in item.keys() else [""]
            effect = item["effect"] if "effect" in item.keys() else [""]
            duration = item["duration"] if "duration" in item.keys() else [""]
            radius = item["radius"] if "radius" in item.keys() else [""]
            chance = item["chance"] if "chance" in item.keys() else [""]
            needs_ai = item["needs_ai"] if "needs_ai" in item.keys() else None
            target_self = item["target_self"] if "target_self" in item.keys() else None

            a = Ability(name=name, description=description, skill_type=skill_type, damage=damage,
                        effect=effect, duration=duration, radius=radius, chance=chance, needs_ai=needs_ai,
                        target_self=target_self)

            self.add_item(a)

    def add_item(self, item):
        """Used when adding initial abilities"""
        self.items.append(item)

    def learn(self, item):
        """Used when learning new abilities"""
        results = []

        if self.capacity and len(self.items) >= self.capacity:
            results.append("You can't learn any more abilities.")

        else:
            results.append("You learn the {0}!".format(item.name))
            self.items.append(item)

        return results
