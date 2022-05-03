from components.abilities import Abilities
from components.fighter import Fighter
from data import json_data
from map_objects import tilemap
import numpy as np

from ui.menus import MenuData
from ui.message import Message


class Player:
    def __init__(self, spirit_power):
        self.owner = None
        self.spirit_power = spirit_power
        self.char = {"player": tilemap.data.tiles["player"]}
        self.char_exp = {"player": 0}
        self.char_level = 1
        self.skill_points = 0
        self.avatar_exp_to_spend = 0
        self.exp_lvl_interval = 10
        self.avatar_exp_lvl_intervals = (25, 75, 200)
        self.insights = 0
        self.avatar = {"player": None}
        self.max_lvl_avatars = ["player"]
        self.sel_weapon = None
        self.sel_attack = None
        self.sel_utility = None
        self.sel_weapon_idx = 0
        self.sel_attack_idx = 0
        self.sel_utility_idx = 0

    def handle_player_exp(self, killed_fighter):
        exp_messages = []
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

        if entity_name not in self.max_lvl_avatars:
            if entity_name in self.char_exp.keys():
                exp_to_spend = 5
            else:
                self.char_exp[entity_name] = 0
                exp_to_spend = 10
                avatar_f_data = json_data.data.fighters[entity_name]
                a_fighter_component = Fighter(hp=avatar_f_data["hp"], ac=avatar_f_data["ac"], ev=avatar_f_data["ev"],
                                              atk=avatar_f_data["atk"], mv_spd=avatar_f_data["mv_spd"],
                                              atk_spd=avatar_f_data["atk_spd"], size=avatar_f_data["size"],
                                              fov=avatar_f_data["fov"], level=0)
                self.avatar[entity_name] = a_fighter_component
                self.avatar[entity_name].owner = self.owner

            lvl_up_msg = self.handle_avatar_exp(entity_name, exp_to_spend)
            exp_messages.extend(lvl_up_msg)

        if levels_gained >= 1:
            self.char_level += levels_gained
            self.skill_points += levels_gained
            self.avatar_exp_to_spend += self.char_level * 10
            exp_messages.append(Message("You have gained a level! Press F2 to level up.", style="level_up"))

        return exp_messages

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

    def handle_avatar_exp(self, entity_name, exp_to_spend=0):
        msgs = []
        max_lvl_msg = None
        if entity_name in self.max_lvl_avatars:
            return msgs
        avatar = self.avatar[entity_name]
        avatar_lvl = avatar.level
        exp_intervals = self.avatar_exp_lvl_intervals
        current_avatar_exp = self.char_exp[entity_name]
        if exp_to_spend == 0:
            exp_to_spend = self.avatar_exp_to_spend
        potential_exp = current_avatar_exp + exp_to_spend
        potential_levels = 0
        self.char_exp[entity_name] += exp_to_spend

        for interval in exp_intervals[avatar_lvl:]:
            if potential_exp >= interval:
                potential_levels += 1
            else:
                break
        if avatar_lvl + potential_levels >= len(exp_intervals):
            avatar.level = len(exp_intervals)
            self.max_lvl_avatars.append(entity_name)
            max_lvl_msg = Message(msg="Your bond with {0} has reached the maximum level!".format(
                entity_name), style="level_up")
        else:
            avatar.level += potential_levels
            msg = Message(msg="Your bond with {0} grows stronger..! The {0} grants you insight into new skills.".format(
                entity_name), style="level_up")
            msgs.append(msg)

        if max_lvl_msg:
            msgs.append(max_lvl_msg)

        self.avatar_exp_to_spend = 0

        return msgs
