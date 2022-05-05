from random import sample, shuffle

from components.ability import Ability
from data import json_data
from ui.message import Message


class Abilities:
    def __init__(self, entity, name=None, capacity=None):
        self.owner = entity
        if name:
            self.name = name
        else:
            self.name = entity.name
        self.capacity = capacity
        self.items = []
        self.weapon_skills = []
        self.attack_skills = []
        self.utility_skills = []
        self.learnable = {}
        self.unlocked = []
        self.initial_abilities_max = 2

        if entity.name != "player":
            self.initialize_abilities()

    def set_learnable(self, entity_name):
        item = json_data.data.fighters[entity_name]
        abilities = item["player_abilities"] if "player_abilities" in item.keys() else item["abilities"]
        learned = [x.name for x in self.items]
        learnable = list(filter(lambda x: x not in learned, abilities))
        shuffle(learnable)
        self.learnable[entity_name] = learnable

    def initialize_abilities(self, entity_name=None, ability_name=None, learn=True):
        if entity_name is None:
            entity_name = self.name
        if ability_name:
            initial_abilities = [ability_name]
        else:
            if self.owner and self.owner.player:
                abilities = json_data.data.fighters[entity_name]["player_abilities"]
                initial_abilities = sample(abilities[1:], self.initial_abilities_max)
                initial_abilities.append(abilities[0])
                self.learnable[entity_name] = list(set(initial_abilities) ^ set(abilities))
                shuffle(self.learnable[entity_name])
            else:
                initial_abilities = json_data.data.fighters[entity_name]["abilities"]
        for n in initial_abilities:
            item = json_data.data.abilities[n]
            skill_type = item["skill_type"]
            # if self.owner and self.owner.player and skill_type != "weapon":
            #     continue
            name = item["name"]
            description = item["description"]
            damage = item["damage"] if "damage" in item.keys() else []
            rank = 0
            icon = item["icon"] if "icon" in item.keys() else 12
            dps = item["dps"] if "dps" in item.keys() else []
            effect = item["effect"] if "effect" in item.keys() else []
            duration = item["duration"] if "duration" in item.keys() else []
            radius = item["radius"] if "radius" in item.keys() else []
            power = item["power"] if "power" in item.keys() else None
            chance = item["chance"] if "chance" in item.keys() else [1.0]
            color = item["color"] if "color" in item.keys() else None
            efx_icons = item["efx_icons"] if "efx_icons" in item.keys() else None
            needs_ai = item["needs_ai"] if "needs_ai" in item.keys() else None
            target_self = item["target_self"] if "target_self" in item.keys() else False
            target_other = item["target_other"] if "target_other" in item.keys() else False
            requires_targeting = item["requires_targeting"] if "requires_targeting" in item.keys() else False
            player_only = item["player_only"] if "player_only" in item.keys() else False
            targets_fighters_only = item["targets_fighters_only"] if "targets_fighters_only" in item.keys() else True
            target_area = item["target_area"] if "target_area" in item.keys() else "disc"
            summoned_entities = item["summoned_entities"] if "summoned_entities" in item.keys() else None

            a = Ability(name=name, description=description, skill_type=skill_type, damage=damage, rank=rank,
                        icon=icon, dps=dps, effect=effect, duration=duration, radius=radius, chance=chance,
                        needs_ai=needs_ai, target_self=target_self, target_other=target_other,
                        player_only=player_only, power=power, requires_targeting=requires_targeting,
                        targets_fighters_only=targets_fighters_only, target_area=target_area,
                        summoned_entities=summoned_entities, color=color, efx_icons=efx_icons, owner=self.owner)
            if learn:
                self.add_item(a)
            else:
                return a

    def add_item(self, item):
        """Used when adding initial abilities"""
        if item.skill_type == "weapon":
            self.weapon_skills.append(item)
        elif item.skill_type == "attack":
            self.attack_skills.append(item)
        elif item.skill_type == "utility":
            self.utility_skills.append(item)

        if self.owner and self.owner.player:
            if item.skill_type == "weapon" and not self.owner.player.sel_weapon:
                self.owner.player.sel_weapon = item
            if item.skill_type == "attack" and not self.owner.player.sel_attack:
                self.owner.player.sel_attack = item
            if item.skill_type == "utility":
                if not self.owner.player.sel_utility:
                    self.owner.player.sel_utility = item
                # blt.TK_1 == 30, map first ability to blt.TK_1
                item.blt_input = len(self.utility_skills) - 1 + 30

        self.items.append(item)

    def learn(self, ability_name=None):
        """Used when learning new abilities"""
        results = []

        if self.capacity and len(self.items) >= self.capacity:
            results.append(Message(msg="You can't learn any more abilities.", style="level_up"))

        else:
            item = ability_name
            results.append(Message(msg="You learn the {0}!".format(item), style="level_up"))
            self.initialize_abilities(ability_name=item)
            unlocked = next((x for x in self.unlocked if x.name == item), False)
            if unlocked:
                self.unlocked.remove(unlocked)

        return results

    def unlock(self, entity_name=None, ability_name=None):
        """Unlocking makes abilities available for learning by using skill points"""
        results = []

        if entity_name:
            item = self.learnable[entity_name].pop(0)
        else:
            item = ability_name
        results.append(Message(msg="You have unlocked the {0}!".format(item), style="level_up"))
        skill = self.initialize_abilities(ability_name=item, learn=False)
        unlocked = next((x for x in self.unlocked if x.name == skill.name), False)
        if not unlocked:
            self.unlocked.append(skill)

        return results

    def learn_or_rank_up(self, ability_name):
        results = []
        for skill in self.items:
            if skill.name == ability_name:
                skill.rank_up()
                msg = Message(
                    msg="You have learned {0} (rank {1})!".format(
                        ability_name, skill.rank), style="level_up")
                results.append(msg)
                break

        if not results:
            results.extend(self.learn(ability_name=ability_name))

        self.owner.player.skill_points -= 1

        return results
