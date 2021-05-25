from components.ability import Ability
from data import json_data


class Abilities:
    def __init__(self, name, capacity=None):
        self.owner = None
        self.name = name
        self.capacity = capacity
        self.items = []

        if name != "player":
            self.initialize_abilities()

    def initialize_abilities(self, name=None):
        if name is None:
            name = self.name
        if self.owner and self.owner.player:
            initial_abilities = json_data.data.fighters[name]["player_abilities"]
            for n in initial_abilities:
                item = json_data.data.abilities[n]
                skill_type = item["skill_type"]
                if skill_type != "weapon":
                    continue
                name = item["name"]
                description = item["description"]
                damage = item["damage"] if "damage" in item.keys() else []
                dps = item["dps"] if "dps" in item.keys() else []
                effect = item["effect"] if "effect" in item.keys() else []
                duration = item["duration"] if "duration" in item.keys() else []
                radius = item["radius"] if "radius" in item.keys() else []
                chance = item["chance"] if "chance" in item.keys() else [1.0]
                needs_ai = item["needs_ai"] if "needs_ai" in item.keys() else None
                target_self = item["target_self"] if "target_self" in item.keys() else None
                target_other = item["target_other"] if "target_other" in item.keys() else None
                player_only = item["player_only"] if "player_only" in item.keys() else False

                a = Ability(name=name, description=description, skill_type=skill_type, damage=damage, dps=dps,
                            effect=effect, duration=duration, radius=radius, chance=chance, needs_ai=needs_ai,
                            target_self=target_self, target_other=target_other, player_only=player_only)

                self.add_item(a)
                self.owner.player.default_attack = a
        else:
            initial_abilities = json_data.data.fighters[name]["abilities"]

            for n in initial_abilities:
                item = json_data.data.abilities[n]
                name = item["name"]
                description = item["description"]
                skill_type = item["skill_type"]
                damage = item["damage"] if "damage" in item.keys() else []
                dps = item["dps"] if "dps" in item.keys() else []
                effect = item["effect"] if "effect" in item.keys() else []
                duration = item["duration"] if "duration" in item.keys() else []
                radius = item["radius"] if "radius" in item.keys() else []
                chance = item["chance"] if "chance" in item.keys() else [1.0]
                needs_ai = item["needs_ai"] if "needs_ai" in item.keys() else None
                target_self = item["target_self"] if "target_self" in item.keys() else None
                target_other = item["target_other"] if "target_other" in item.keys() else None
                player_only = item["player_only"] if "player_only" in item.keys() else False

                a = Ability(name=name, description=description, skill_type=skill_type, damage=damage, dps=dps,
                            effect=effect, duration=duration, radius=radius, chance=chance, needs_ai=needs_ai,
                            target_self=target_self, target_other=target_other, player_only=player_only)

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
