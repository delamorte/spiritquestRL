from math import ceil
from random import random

from game_states import GameStates
from helpers import roll_dice


class StatusEffect:
    def __init__(self, owner, source, name, description=None, dps=None, delayed_damage=None, rank=None,
                 fly=None, sneak=None, reveal=None, invisibility=None, slow=None, drain_stats=None,
                 hit_penalty=None, paralyze=None, duration=None, chance=None, color=None, power=None,
                 heal=None):
        self.owner = owner
        self.source = source
        self.name = name
        self.description = description
        self.dps = dps
        self.delayed_damage = delayed_damage
        self.fly = fly
        self.fly_ev_boost = 0
        self.sneak = sneak
        self.reveal = reveal
        self.slow = slow
        self.invisibility = invisibility
        self.rank = rank
        self.color = color
        self.drain_stats = drain_stats
        self.hit_penalty = hit_penalty
        self.paralyze = paralyze
        self.duration = duration
        self.chance = chance
        self.power = power
        self.heal = heal
        self.slow_amount = None

    def process(self):
        msg = None
        if self.source.dead and self.name == "strangle":
            self.duration = 0

        if self.heal:
            msg = self.owner.heal(self.power[self.rank])
            return self, msg

        if self.duration <= 0:

            if self.hit_penalty:
                self.owner.hit_penalty -= self.hit_penalty[self.rank]
            if self.drain_stats:
                self.owner.ac += self.drain_stats[self.rank]
                self.owner.ev += self.drain_stats[self.rank]
            if self.slow_amount:
                self.owner.mv_spd += self.slow_amount
            if self.delayed_damage:
                self.owner.take_damage(self.delayed_damage)
            if self.paralyze:
                self.owner.paralyzed = False
            if self.fly:
                self.owner.ev -= self.fly_ev_boost
                self.owner.flying = False
            self.owner.effects.remove(self.description)
            return self, msg

        if self.dps:
            self.owner.take_damage(self.dps[self.rank])

        if self.hit_penalty:
            if self.description not in self.owner.effects:
                self.owner.hit_penalty += self.hit_penalty[self.rank]

        if self.drain_stats:
            if self.description not in self.owner.effects:
                self.owner.hit_penalty -= self.drain_stats[self.rank]
                self.owner.ac -= self.drain_stats[self.rank]
                self.owner.ev -= self.drain_stats[self.rank]

        if self.slow:
            if self.description not in self.owner.effects:
                self.slow_amount = self.owner.mv_spd - self.owner.mv_spd * self.slow[self.rank]
                self.owner.mv_spd -= self.slow_amount

        if self.paralyze:
            if random() <= self.chance[self.rank]:
                self.owner.paralyzed = True
            else:
                self.owner.paralyzed = True

        if self.fly:
            if self.description not in self.owner.effects:
                self.fly_ev_boost = ceil(self.owner.ev * self.power[self.rank] - self.owner.ev)
                self.owner.ev += self.fly_ev_boost
                self.owner.flying = True

        if self.description not in self.owner.effects:
            self.owner.effects.append(self.description)
        self.duration -= 1

        return None, msg
