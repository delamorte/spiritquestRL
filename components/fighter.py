from components.animation import Animation
from helpers import roll_dice
from math import ceil
from random import randint, choice
from components.status_effect import StatusEffect
from data import json_data
from ui.message import Message


class Fighter:
    def __init__(self, hp, ac, ev, atk, mv_spd, atk_spd, size, level=1, fov=6):
        self.owner = None
        self.max_hp = hp
        self.hp = hp
        self.ac = ac
        self.ev = ev
        self.hit_penalty = 0
        self.atk = atk
        self.str_bonus = ceil(atk / 2 - 1)
        if self.str_bonus <= 0:
            self.str_bonus = 0
        self.mv_spd = mv_spd
        self.atk_spd = atk_spd
        self.level = level
        self.fov = fov
        self.size = size

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.owner.dead = True

    def heal(self, power):
        result = None
        amount = roll_dice(power)
        if self.hp >= self.max_hp:
            result = Message("{0} is already at max health.".format(self.owner.colored_name), extend_line=True)
            return result
        else:
            if self.hp + amount > self.max_hp:
                self.hp = self.max_hp
            else:
                self.hp += amount
        return result

    def leap(self, game_map, skill):
        results = []
        neighbours = game_map.get_neighbours(self.owner, radius=skill.radius[skill.rank], algorithm="square",
                                             empty_tiles=True)
        leap_tile = choice(neighbours)
        self.owner.move_to_tile(leap_tile.x, leap_tile.y)
        msg = Message(msg="The {0} leaps to a safe distance!".format(self.owner.colored_name))
        results.append(msg)
        self.owner.animations.buffer.append(Animation(self.owner, self.owner, skill, target_self=True))
        return results

    def use_skill(self, target, skill, game_map=None):
        results = []
        if skill.name == "leap" and not self.owner.player:
            results.extend(self.leap(game_map, skill))
            return results

        hit_chance = randint(1, 100)
        miss = (target.fighter.ev * 2) >= hit_chance - self.hit_penalty
        if (skill.skill_type == "attack" or skill.skill_type == "utility") and self.owner.player:
            miss = False

        if skill is not None:
            if skill.skill_type == "attack" or skill.skill_type == "weapon":
                if miss:
                    if self.owner.player:
                        msg = Message(msg="You attack the {0} with {1}, but miss.".format(
                            target.name.lower(), skill.name),
                                      style="miss")
                        results.append(msg)
                    else:
                        msg = Message(msg="The {0} attacks the {1} with {2}, but misses.".format(
                            self.owner.name, target.colored_name.lower(), skill.name),
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
                            drain_atk = json_efx["drain_atk"] if "drain_atk" in json_efx.keys() else []
                            boost_atk = json_efx["boost_atk"] if "boost_atk" in json_efx.keys() else []
                            boost_ac = json_efx["boost_ac"] if "boost_ac" in json_efx.keys() else []
                            boost_ev = json_efx["boost_ev"] if "boost_ev" in json_efx.keys() else []
                            boost_hp = json_efx["boost_hp"] if "boost_hp" in json_efx.keys() else []
                            description = json_efx["description"]
                            paralyze = json_efx["paralyze"] if "paralyze" in json_efx.keys() else False
                            stun = json_efx["stun"] if "stun" in json_efx.keys() else False
                            color = json_efx["color"] if "color" in json_efx.keys() else None
                            chance = json_efx["chance"]
                            power = json_efx["power"] if "power" in json_efx.keys() else None
                            effect_component = StatusEffect(owner=target.status_effects, source=self, name=effect, duration=duration, slow=slow, dps=dps,
                                                            delayed_damage=delayed_damage,  rank=rank, drain_stats=drain_stats,
                                                            hit_penalty=hit_penalty, paralyze=paralyze, description=description,
                                                            chance=chance, color=color, power=power, drain_atk=drain_atk,
                                                            boost_atk=boost_atk, boost_ac=boost_ac, boost_hp=boost_hp,
                                                            boost_ev=boost_ev, stun=stun)

                            target.status_effects.add_item(effect_component)
                            msg = Message(msg="The {0} is inflicted with {1}!".format(
                                target.colored_name.lower(), effect), color=color)
                            results.append(msg)

                    if damage > 0:
                        target.fighter.take_damage(damage)

                    else:
                        if self.owner.player:
                            msg = Message(msg="You attack the {0} with {1} but do no damage.".format(
                                target.colored_name.lower(), skill.name), style="miss", extend_line=True)
                            results.append(msg)
                        else:
                            msg = Message(msg="The {0} attacks the {1} with {2} but does no damage.".format(
                                self.owner.colored_name, target.colored_name.lower(), skill.name), style="miss", extend_line=True)
                            results.append(msg)
                self.owner.animations.buffer.append(Animation(self.owner, target, skill, target_self=skill.target_self))

            elif skill.skill_type == "utility":
                if skill.player_only and not self.owner.player:
                    return results

                else:
                    damage = self.calculate_damage(skill, target)
                    if skill.effect:
                        for effect in skill.effect:

                            json_efx = json_data.data.status_effects[effect]
                            description = json_efx["description"]

                            if target.status_effects.has_effect(description):
                                results.append(Message("The {0} is already {1}!".format(target.colored_name.lower(), description)))
                                continue

                            duration = roll_dice(skill.duration[skill.rank])
                            fly = skill if effect == "fly" else None
                            sneak = skill if effect == "sneak" else None
                            reveal = skill if effect == "reveal" else None
                            heal = skill if effect == "heal" else None
                            summon = skill.summoned_entities if skill.summoned_entities else None
                            invisibility = skill if skill.name == "invisibility" else None
                            drain_atk = skill if skill.name == "drain atk" else None
                            boost_atk = skill if skill.name == "boost atk" else None
                            boost_ac = skill if skill.name == "boost ac" else None
                            boost_ev = skill if skill.name == "boost ev" else None
                            boost_hp = skill if skill.name == "boost hp" else None
                            color = json_efx["color"] if "color" in json_efx.keys() else None

                            if skill.power:
                                power = skill.power
                            else:
                                power = json_efx["power"] if "power" in json_efx.keys() else None
                            rank = skill.rank

                            effect_component = StatusEffect(owner=target.status_effects, source=self, name=effect,
                                                            duration=duration, fly=fly, sneak=sneak, reveal=reveal,
                                                            invisibility=invisibility, description=description,
                                                            color=color, power=power, rank=rank, heal=heal,
                                                            summon=summon, drain_atk=drain_atk,
                                                            boost_atk=boost_atk, boost_ac=boost_ac, boost_hp=boost_hp,
                                                            boost_ev=boost_ev)

                            target.status_effects.add_item(effect_component)
                            results.extend(self.hit_messages(skill, target, damage))
                            self.owner.animations.buffer.append(
                                Animation(self.owner, target, skill, target_self=skill.target_self))

                    else:
                        if damage > 0:
                            target.fighter.take_damage(damage)
                            results.extend(self.hit_messages(skill, target, damage))
                            self.owner.animations.buffer.append(
                                Animation(self.owner, target, skill, target_self=skill.target_self))

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
                    msg = Message(msg="You use {0}!".format(
                        skill.name), style="skill_use")
                else:
                    msg = Message(msg="You use {0} on {1}!".format(
                        skill.name, target.colored_name.lower()), style="skill_use")
                results.append(msg)
                if damage > 0:
                    if skill.name == "heal" and target == self.owner:
                        msg = Message(msg="You heal yourself for {0} hit points.".format(
                            str(-1*damage)), extend_line=True)

                    elif skill.name == "heal":
                        msg = Message(msg="You heal the {0} for {1} hit points.".format(
                            target.colored_name.lower(), str(-1*damage)), extend_line=True)

                    else:
                        msg = Message(msg="You attack the {0} for {1} damage.".format(
                            target.colored_name.lower(), str(damage)), extend_line=True)
                    results.append(msg)
            else:
                msg = Message(msg="You attack the {0} with {1} for {2} damage.".format(
                    target.colored_name.lower(), skill.name, damage))
                results.append(msg)

        else:
            if skill.skill_type != "weapon":
                if target == self.owner:
                    msg = Message(msg="The {0} uses {1} on itself!".format(
                        self.owner.colored_name.lower(), skill.name), style="skill_use")
                else:
                    msg = Message(msg="The {0} uses {1} on {2}!".format(
                        self.owner.colored_name.lower(), skill.name, target.colored_name.lower()), style="skill_use")
                results.append(msg)
                if damage > 0:
                    if skill.name == "heal" and target == self.owner:
                        msg = Message(msg="The {0} heals itself for {1} hit points.".format(
                            self.owner.colored_name.lower(), str(-1*damage)), extend_line=True)

                    elif skill.name == "heal":
                        msg = Message(msg="The {0} heals {1} for {2} hit points.".format(
                            self.owner.colored_name.lower(), target.colored_name.lower(), str(-1*damage)), extend_line=True)
                    else:
                        msg = Message(msg="The {0} attacks the {1} for {2} damage.".format(
                            self.owner.colored_name.lower(), target.colored_name.lower(), str(damage)), extend_line=True)
                    results.append(msg)
            else:
                msg = Message(msg="The {0} attacks the {1} with {2} for {3} damage.".format(
                    self.owner.colored_name.lower(), target.colored_name.lower(), skill.name, damage))
                results.append(msg)

        return results
