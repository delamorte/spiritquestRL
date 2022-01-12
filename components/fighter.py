from helpers import roll_dice
from math import ceil
from random import randint
from components.status_effect import StatusEffect
from data import json_data
from ui.message import Message


class Fighter:
    def __init__(self, hp, ac, ev, power, mv_spd, atk_spd, size, level=1, fov=6):
        self.owner = None
        self.max_hp = hp
        self.hp = hp
        self.ac = ac
        self.ev = ev
        self.hit_penalty = 0
        self.power = power
        self.str_bonus = ceil(power / 2 - 1)
        if self.str_bonus <= 0:
            self.str_bonus = 0
        self.mv_spd = mv_spd
        self.atk_spd = atk_spd
        self.level = level
        self.fov = fov
        self.size = size
        self.dead = False
        self.paralyzed = False
        self.flying = False
        self.effects = []

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.dead = True

    def heal(self, power):
        result = None
        amount = roll_dice(power)
        if self.hp >= self.max_hp:
            result = Message("{0} is already at max health.".format(self.owner.name.capitalize()), extend_line=True)
            return result
        else:
            if self.hp + amount > self.max_hp:
                self.hp = self.max_hp
            else:
                self.hp += amount
        return result

    def attack(self, target, skill):
        results = []
        hit_chance = randint(1, 100)
        miss = (target.fighter.ev * 2) >= hit_chance - self.hit_penalty
        if (skill.skill_type == "attack" or skill.skill_type == "utility") and self.owner.player:
            miss = False

        if skill is not None:
            if skill.skill_type == "attack" or skill.skill_type == "weapon":
                if miss:
                    if self.owner.player:
                        msg = Message(msg="You attack the {0} with {1}, but miss.".format(
                            target.name, skill.name),
                                      style="miss")
                        results.append(msg)
                    else:
                        msg = Message(msg="The {0} attacks you with {1}, but misses.".format(
                            self.owner.name, skill.name),
                                      style="miss")
                        results.append(msg)
                else:
                    damage = self.calculate_damage(skill, target)
                    results = self.hit_messages(skill, target, damage)

                    if skill.effect:
                        for effect in skill.effect:
                            json_efx = json_data.data.status_effects[effect]
                            if skill.duration:
                                duration = roll_dice(skill.duration[skill.rank])
                            else:
                                duration = roll_dice(json_efx["duration"][skill.rank])
                            hit_penalty = json_efx["hit_penalty"] if "hit_penalty" in json_efx.keys() else []
                            if "delayed_damage" in json_efx.keys():
                                delayed_damage = roll_dice(json_efx["delayed_damage"][skill.rank])
                            else:
                                delayed_damage = []
                            rank = skill.rank
                            dps = json_efx["dps"] if "dps" in json_efx.keys() else []
                            slow = json_efx["slow"] if "slow" in json_efx.keys() else []
                            drain_stats = json_efx["drain_stats"] if "drain_stats" in json_efx.keys() else []
                            description = json_efx["description"]
                            paralyze = json_efx["paralyze"] if "paralyze" in json_efx.keys() else False
                            color = json_efx["color"] if "color" in json_efx.keys() else None
                            chance = json_efx["chance"]
                            power = json_efx["power"] if "power" in json_efx.keys() else None
                            effect_component = StatusEffect(owner=target.fighter, source=self, name=effect, duration=duration, slow=slow, dps=dps,
                                                            delayed_damage=delayed_damage,  rank=rank, drain_stats=drain_stats,
                                                            hit_penalty=hit_penalty, paralyze=paralyze, description=description,
                                                            chance=chance, color=color, power=power)

                            target.status_effects.add_item(effect_component)
                            if self.owner.player:
                                msg = Message(msg="The {0} is inflicted with {1}!".format(
                                    target.name, effect), color=color)
                                results.append(msg)
                            else:
                                msg = Message(msg="You are inflicted with {} !".format(
                                    effect), color=color)
                                results.append(msg)

                    if damage > 0:
                        target.fighter.take_damage(damage)

                    else:
                        if self.owner.player:
                            msg = Message(msg="You attack the {0} with {1} but do no damage.".format(
                                target.name, skill.name), style="miss", extend_line=True)
                            results.append(msg)
                        else:
                            msg = Message(msg="The {0} attacks you  with {1} but does no damage.".format(
                                self.owner.name, skill.name), style="miss", extend_line=True)
                            results.append(msg)

            elif skill.skill_type == "utility":
                if skill.player_only and not self.owner.player:
                    return results

                else:
                    damage = self.calculate_damage(skill, target)
                    if skill.effect:
                        for effect in skill.effect:

                            json_efx = json_data.data.status_effects[effect]
                            description = json_efx["description"]

                            if description in self.effects:
                                results.append(Message("Target is already {0}!".format(description)))
                                continue

                            duration = roll_dice(skill.duration[skill.rank])
                            fly = skill if skill.name == "fly" else None
                            sneak = skill if skill.name == "sneak" else None
                            reveal = skill if skill.name == "reveal" else None
                            heal = skill if skill.name == "heal" else None
                            invisibility = skill if skill.name == "invisibility" else None
                            color = json_efx["color"] if "color" in json_efx.keys() else None
                            if skill.power:
                                power = skill.power
                            else:
                                power = json_efx["power"] if "power" in json_efx.keys() else None
                            rank = skill.rank

                            effect_component = StatusEffect(owner=target.fighter, source=self, name=effect,
                                                            duration=duration, fly=fly, sneak=sneak, reveal=reveal,
                                                            invisibility=invisibility, description=description,
                                                            color=color, power=power, rank=rank, heal=heal)

                            target.status_effects.add_item(effect_component)
                            msgs = None
                            if target == self.owner:
                                msgs = self.owner.status_effects.process_effects(effect_component)

                            results.extend(self.hit_messages(skill, target, damage))
                            if msgs:
                                results.extend(msgs)

                    else:
                        if damage > 0:
                            target.fighter.take_damage(damage)
                            results.extend(self.hit_messages(skill, target, damage))

        return results

    def calculate_damage(self, skill, target):
        if not skill.damage:
            return 0
        damage_str = skill.damage[skill.rank]
        ac = target.fighter.ac
        str_bonus = self.str_bonus
        if skill.skill_type == "utility":
            ac = 0
            str_bonus = 0
        damage = roll_dice(damage_str) + str_bonus - ac
        return int(ceil(damage))

    def hit_messages(self, skill, target, damage):
        results = []
        if self.owner.player:
            if skill.skill_type != "weapon":
                if target == self.owner:
                    msg = Message(msg="You use {0} on yourself!".format(
                        skill.name), style="skill_use")
                else:
                    msg = Message(msg="You use {0} on {1}!".format(
                        skill.name, target.name), style="skill_use")
                results.append(msg)
                if damage > 0:
                    if skill.name == "heal" and target == self.owner:
                        msg = Message(msg="You heal yourself for {0} hit points.".format(
                            str(-1*damage)), extend_line=True)

                    elif skill.name == "heal":
                        msg = Message(msg="You heal the {0} for {1} hit points.".format(
                            target.name, str(-1*damage)), extend_line=True)

                    else:
                        msg = Message(msg="You attack the {0} for {1} damage.".format(
                            target.name, str(damage)), style="attack", extend_line=True)
                    results.append(msg)
            else:
                msg = Message(msg="You attack the {0} with {1} for {2} damage.".format(
                    target.name, skill.name, damage))
                results.append(msg)

        else:
            if skill.skill_type != "weapon":
                if target == self.owner:
                    msg = Message(msg="The {0} uses {1} on itself!".format(
                        self.owner.name, skill.name), style="skill_use")
                else:
                    msg = Message(msg="The {0} uses {1} on you!".format(
                        self.owner.name, skill.name), style="skill_use")
                results.append(msg)
                if damage > 0:
                    if skill.name == "heal" and target == self.owner:
                        msg = Message(msg="The {0} heals itself for {1} hit points.".format(
                            self.owner.name, str(-1*damage)), style="attack", extend_line=True)

                    elif skill.name == "heal":
                        msg = Message(msg="The {0} heals for {1} for {2} hit points.".format(
                            self.owner.name, target.name, str(-1*damage)), style="attack", extend_line=True)
                    else:
                        msg = Message(msg="The {0} attacks you for {1} damage.".format(
                            self.owner.name, str(damage)), style="attack", extend_line=True)
                    results.append(msg)
            else:
                msg = Message(msg="The {0} attacks you with {1} for {2} damage.".format(
                    self.owner.name, skill.name, damage))
                results.append(msg)

        return results
