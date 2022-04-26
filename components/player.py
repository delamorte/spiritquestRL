from map_objects import tilemap
import numpy as np

from ui.message import Message


class Player:
    def __init__(self, spirit_power):
        self.owner = None
        self.spirit_power = spirit_power
        self.char = {"player": tilemap.data.tiles["player"]}
        self.char_exp = {"player": 0}
        self.char_level = 1
        self.skill_points = 0
        self.exp_lvl_interval = 100
        self.insights = 0
        self.avatar = {"player": None}
        self.sel_weapon = None
        self.sel_attack = None
        self.sel_utility = None
        self.sel_weapon_idx = 0
        self.sel_attack_idx = 0
        self.sel_utility_idx = 0

    def handle_player_exp(self, killed_fighter):
        self.spirit_power += killed_fighter.max_hp
        self.char_exp["player"] += killed_fighter.max_hp
        self.owner.fighter.hp += killed_fighter.atk
        levels_gained = int(self.char_exp["player"] / (self.exp_lvl_interval * self.char_level))
        entity_name = killed_fighter.owner.name

        if entity_name in tilemap.data.tiles["monsters"].keys():
            self.char[entity_name] = tilemap.data.tiles["monsters"][entity_name]
        elif entity_name in tilemap.data.tiles["monsters_light"].keys():
            self.char[entity_name] = tilemap.data.tiles["monsters_light"][entity_name]
        elif entity_name in tilemap.data.tiles["monsters_chaos"].keys():
            self.char[entity_name] = tilemap.data.tiles["monsters_chaos"][entity_name]

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
            results = self.owner.fighter.use_skill(target, ability)
            msgs = self.owner.status_effects.process_effects(game_map=game_map, self_targeting=True)
            if msgs:
                results.extend(msgs)

        elif not target:
            radius = ability.get_range()

            entities = game_map.get_neighbours(self.owner, radius, fighters=True,
                                               include_self=include_self, algorithm=area,
                                               mark_area=True)
            if not entities and not include_self:
                msg = Message("There are no available targets in range.")
                results.append(msg)
            elif len(entities) == 1 and not ability.requires_targeting:
                target = entities[0]
                results = self.owner.fighter.use_skill(target, ability)
            else:
                msg = Message(msg="Use '{0}' on which target? Range: {1}".format(
                    ability.name, radius), style="question")
                results.append(msg)
                target = entities[0]
                targeting = True
        else:
            results = self.owner.fighter.use_skill(target, ability)

        return results, target, targeting
