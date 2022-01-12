from components.entity import get_neighbour_entities
from map_objects.tilemap import tilemap
import numpy as np

from ui.message import Message


class Player:
    def __init__(self, spirit_power):
        self.owner = None
        self.spirit_power = spirit_power
        self.char = {"player": tilemap()["player"]}
        self.char_exp = {"player": 0}
        self.char_level = 1
        self.skill_points = 0
        self.exp_lvl_interval = 100
        self.insights = 0
        self.avatar = {"player": None}
        self.lightmap = None
        self.sel_weapon = None
        self.sel_attack = None
        self.sel_utility = None
        self.sel_weapon_idx = 0
        self.sel_attack_idx = 0
        self.sel_utility_idx = 0

    def init_light(self):
        self.lightmap = np.ones_like(self.owner.light_source.fov_map.fov, dtype=float)

    def calculate_light(self):
        pass

    def handle_player_exp(self, killed_fighter):
        self.spirit_power += killed_fighter.max_hp
        self.char_exp["player"] += killed_fighter.max_hp
        self.owner.fighter.hp += killed_fighter.power
        levels_gained = int(self.char_exp["player"] / (self.exp_lvl_interval * self.char_level))
        entity_name = killed_fighter.owner.name

        if entity_name in tilemap()["monsters"].keys():
            self.char[entity_name] = tilemap()["monsters"][entity_name]
        elif entity_name in tilemap()["monsters_light"].keys():
            self.char[entity_name] = tilemap()["monsters_light"][entity_name]
        elif entity_name in tilemap()["monsters_chaos"].keys():
            self.char[entity_name] = tilemap()["monsters_chaos"][entity_name]

        if entity_name in self.char_exp.keys():
            self.char_exp[entity_name] += 1
        else:
            self.char_exp[entity_name] = 1

        if levels_gained >= 1:
            self.level_up(levels_gained)
            return Message("You have gained a level!", style="level_up")

        return None

    def level_up(self, levels_gained):
        self.char_level += levels_gained
        self.skill_points += 1

    def switch_weapon(self):
        idx = self.sel_weapon_idx + 1
        self.sel_weapon_idx += 1
        if idx >= len(self.owner.abilities.weapon_skills):
            idx = 0
            self.sel_weapon_idx = 0
        self.sel_weapon = self.owner.abilities.weapon_skills[idx]

    def switch_attack(self):
        idx = self.sel_attack_idx + 1
        self.sel_attack_idx += 1
        if idx >= len(self.owner.abilities.attack_skills):
            idx = 0
            self.sel_attack_idx = 0
        self.sel_attack = self.owner.abilities.attack_skills[idx]

    def switch_utility(self):
        idx = self.sel_utility_idx + 1
        self.sel_utility_idx += 1
        if idx >= len(self.owner.abilities.utility_skills):
            idx = 0
            self.sel_utility_idx = 0
        self.sel_utility = self.owner.abilities.utility_skills[idx]

    def use_ability(self, game_map, ability, target=None):
        results = []
        targeting = False
        area = ability.target_area
        include_self = ability.target_self

        if include_self:
            target = self.owner

        if not target:
            radius = ability.get_range()

            entities = get_neighbour_entities(self.owner, game_map.tiles, radius, fighters=True,
                                              include_self=include_self, algorithm=area,
                                              mark_area=True)
            if not entities and not include_self:
                msg = Message("There are no available targets in range.")
                results.append(msg)
            elif len(entities) == 1 and not ability.requires_targeting:
                target = entities[0]
                results = self.owner.fighter.attack(target, ability, game_map=game_map.tiles)
            else:
                msg = Message(msg="Use '{0}' on which target? Range: {1}".format(
                    ability.name, radius), style="question")
                results.append(msg)
                target = entities[0]
                targeting = True
        else:
            results = self.owner.fighter.attack(target, ability, game_map=game_map.tiles)

        return results, target, targeting
