from math import ceil
from random import random
from components.entity import get_neighbours
from ui.message import Message


class StatusEffect:
    def __init__(self, owner, source, name, description=None, dps=None, delayed_damage=None, rank=None,
                 fly=None, sneak=None, reveal=None, invisibility=None, slow=None, drain_stats=None,
                 hit_penalty=None, paralyze=None, duration=None, chance=None, color=None, power=None,
                 heal=None, summoning=None, target_self=None):
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
        self.summoning = summoning
        self.target_self = target_self
        self.slow_amount = None
        self.process_instantly = False

        # Process buffs etc. instantly after casting
        if self.fly or self.heal or self.reveal or self.invisibility or self.sneak or self.summoning:
            self.process_instantly = True

    def process(self, game_map=None):
        msg = None

        if self.process_instantly:
            self.process_instantly = False

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
            if self.reveal:
                self.owner.revealing = False
            if self.summoning:
                self.summoning = None
                self.owner.owner.summoner.summoning = None
                self.owner.owner.summoner.rank = self.rank
            self.owner.effects.remove(self.description)
            return self, msg

        if self.summoning:
            self.owner.summoning = True
            self.owner.owner.summoner.summoning = self.summoning
            self.owner.owner.summoner.rank = self.rank

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

        if self.reveal:
            neighbours = get_neighbours(self.owner.owner, game_map.tiles, include_self=False,
                                        fighters=False, mark_area=True,
                                        radius=self.reveal.radius[self.rank], algorithm="square")
            for entity in neighbours:
                if entity.hidden:
                    entity.hidden = False
            if self.description not in self.owner.effects:
                self.owner.revealing = True

        if self.description not in self.owner.effects:
            self.owner.effects.append(self.description)
        self.duration -= 1

        return None, msg
