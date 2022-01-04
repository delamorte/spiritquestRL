from helpers import roll_dice
from math import ceil
from random import randint
from components.status_effect import StatusEffect
from data import json_data


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

        if skill is not None:
            if skill.skill_type == "attack" or skill.skill_type == "weapon":
                damage = self.calculate_damage(skill, target)
                if miss:
                    if self.owner.player:
                        results.append([
                            "You attack the {0} with {1}, but miss.".format(target.name, skill.name), "gray"])
                    else:
                        results.append([
                            "The {0} attacks you with {1}, but misses.".format(self.owner.name, skill.name), "gray"])
                else:
                    if self.owner.player:
                        results.append(["You use {0} on {1}!".format(
                            skill.name, target.name), "orange"])
                    else:
                        results.append(["The {0} uses {1} on you!".format(
                            self.owner.name, skill.name)])

                    if skill.effect:
                        for effect in skill.effect:
                            json_efx = json_data.data.status_effects[effect]
                            if skill.duration:
                                duration = roll_dice(skill.duration[min(self.level-1, 2)])
                            else:
                                duration = roll_dice(json_efx["duration"][min(self.level - 1, 2)])
                            hit_penalty = json_efx["hit_penalty"] if "hit_penalty" in json_efx.keys() else []
                            if "delayed_damage" in json_efx.keys():
                                delayed_damage = roll_dice(json_efx["delayed_damage"][min(self.level - 1, 2)])
                            else:
                                delayed_damage = []
                            rank = min(self.level-1, 2)
                            dps = json_efx["dps"] if "dps" in json_efx.keys() else []
                            slow = json_efx["slow"] if "slow" in json_efx.keys() else []
                            drain_stats = json_efx["drain_stats"] if "drain_stats" in json_efx.keys() else []
                            description = json_efx["description"]
                            paralyze = json_efx["paralyze"] if "paralyze" in json_efx.keys() else False
                            chance = json_efx["chance"]
                            effect_component = StatusEffect(owner=target.fighter, source=self, name=effect, duration=duration, slow=slow, dps=dps,
                                                            delayed_damage=delayed_damage,  rank=rank, drain_stats=drain_stats,
                                                            hit_penalty=hit_penalty, paralyze=paralyze, description=description,
                                                            chance=chance)

                            target.status_effects.add_item(effect_component)
                            if self.owner.player:
                                results.append(["The {0} is inflicted with {1}!".format(target.name, effect)])
                            else:
                                results.append(["You are inflicted with {} !".format(effect), "green"])

                    if damage > 0:
                        if self.owner.player:
                            results[-1][0] += (" You attack the {0} for {1} hit points.".format(
                                target.name, str(damage)))
                        else:
                            results[-1][0] += (" The {0} attacks you for {1} hit points.".format(
                                self.owner.name, str(damage)))

                        results.extend(target.fighter.take_damage(damage))

                    else:
                        if self.owner.player:
                            results[-1][0] += (
                                " You attack the {0} with {1} but do no damage.".format(target.name, skill.name))
                        else:
                            results[-1][0] += (
                                "The {0} attacks you  with {1} but does no damage.".format(self.owner.name, skill.name))
        return results

    def calculate_damage(self, skill, target):
        str_bonus = max(self.power / 2 - 1, 0)
        damage_str = skill.damage[min(self.level - 1, 2)]
        damage = roll_dice(damage_str) + str_bonus - target.fighter.ac
        return int(ceil(damage))
