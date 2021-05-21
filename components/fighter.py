from data import json_data
from helpers import roll_dice
from math import ceil
from random import randint

from components.abilities import Abilities
from components.ability import Ability
from components.status_effect import StatusEffect
from data import json_data
from descriptions import abilities as abilities_db
from game_states import GameStates
import random
import json


class Fighter:
    def __init__(self, hp, ac, ev, power, mv_spd, atk_spd, size, level=1, fov=6):
        self.owner = None
        self.max_hp = hp
        self.hp = hp
        self.ac = ac
        self.ev = ev
        self.hit_penalty = 0
        self.power = power
        self.mv_spd = mv_spd
        self.atk_spd = atk_spd
        self.level = level
        self.fov = fov
        self.size = size
        self.dead = False
        self.paralyzed = False
        self.effects = []

    def take_damage(self, amount):
        results = []
        self.hp -= amount
        if self.hp <= 0:
            self.dead = True
        return results

    def attack(self, target, skill):
        results = []
        hit_chance = randint(1, 100)
        miss = (target.fighter.ev * 2 - self.hit_penalty) >= hit_chance

        if skill.skill_type == "attack" or skill.skill_type == "weapon":
            damage = self.calculate_damage(skill, target)
            if miss:
                if self.owner.player:
                    results.append(
                        "You attack the {0} with {1}, but miss.".format(target.name, skill.name))
                else:
                    results.append(
                        "The {0} attacks you with {1}, but misses.".format(self.owner.name, skill.name))
            else:
                if self.owner.player:
                    results.append("You use {0} on {1}!".format(
                        skill, target.name))
                else:
                    results.append("The {0} uses {1} on you!".format(
                        self.owner.name, skill.name))

                if skill.effect:
                    effect = skill.effect
                    duration = roll_dice(skill.duration[min(self.level-1, 2)])
                    json_efx = json_data.data.status_effects
                    hit_penalty = json_efx[effect]["hit_penalty"] if "hit_penalty" in json_efx.keys() else [0]
                    slow = json_efx[effect]["slow"] if "slow" in json_efx.keys() else [0]
                    dps = json_efx[effect]["dps"] if "dps" in json_efx.keys() else [0]
                    rank = min(self.owner.level-1, 2)
                    drain_stats = json_efx[effect]["drain_stats"] if "drain_stats" in json_efx.keys() else [0]
                    description = json_efx[effect]["description"]
                    paralyze = json_efx[effect]["paralyze"] if "paralyze" in json_efx.keys() else False
                    chance = json_efx[effect]["chance"]
                    effect_component = StatusEffect(owner=self,
                                                    name=effect, duration=duration, slow=slow, dps=dps,
                                                    rank=rank, drain_stats=drain_stats, hit_penalty=hit_penalty,
                                                    paralyze=paralyze, description=description, chance=chance)

                    if self.owner.player:
                        target.owner.status_effects.add_item(effect_component)
                        results.append("The {0} is inflicted with {1}!".format(target.name, effect))
                    else:
                        self.owner.status_effects.add_item(effect_component)
                        results.append("You are inflicted with {} !".format(effect))

                if damage > 0:
                    if self.owner.player:
                        results.append("You attack the {0} for {1} hit points.".format(
                            target.name, str(damage)))
                    else:
                        results.append("The {0} attacks you for {1} hit points.".format(
                            self.owner.name, str(damage)))
                    
                    results.extend(target.fighter.take_damage(damage))

                else:
                    if self.owner.player:
                        results.append(
                            "You attack the {0} with {1} but do no damage.".format(target.name, skill.name))
                    else:
                        results.append(
                            "The {0} attacks you  with {1} but does no damage.".format(self.owner.name, skill.name))
        return results

    def calculate_damage(self, skill, target):
        str_bonus = max(self.power / 2 - 1, 0)
        damage_str = skill.damage[min(self.level - 1, 2)]
        damage = roll_dice(damage_str) + str_bonus - target.fighter.ac
        return int(ceil(damage))
