from game_states import GameStates
from helpers import roll_dice


class StatusEffect:
    def __init__(self, owner, name, description=None, dps=None, rank=None, slow=None, drain_stats=None,
                 hit_penalty=None, paralyze=None, duration=None, chance=None):
        self.owner = owner
        self.name = name
        self.description = description
        self.dps = dps
        self.slow = slow
        self.rank = rank
        self.drain_stats = drain_stats
        self.hit_penalty = hit_penalty
        self.paralyze = paralyze
        self.duration = duration
        self.chance = chance
        self.slow_amount = None

    def process(self):

        if self.description not in self.owner.effects:
            self.owner.effects.append(self.description)

        duration = roll_dice(self.duration)

        if duration <= 0:
            self.owner.hit_penalty -= self.hit_penalty[self.rank]
            self.owner.ac += self.drain_stats[self.rank]
            self.owner.ev += self.drain_stats[self.rank]
            self.owner.mv_spd += self.slow_amount
            if self.paralyze:
                self.owner.paralyzed = False
            return self

        if self.dps:
            self.owner.take_damage(self.dps)
            self.duration -= 1

        if self.hit_penalty:
            self.duration -= 1
            if self.description not in self.owner.effects:
                self.owner.hit_penalty += self.hit_penalty[self.rank]

        if self.drain_stats:
            self.duration -= 1
            if self.description not in self.owner.effects:
                self.owner.hit_penalty -= self.drain_stats[self.rank]
                self.owner.ac -= self.drain_stats[self.rank]
                self.owner.ev -= self.drain_stats[self.rank]

        if self.slow:
            self.duration -= 1
            if self.description not in self.owner.effects:
                self.slow_amount = self.owner.mv_spd - self.owner.mv_spd * self.slow[self.rank]
                self.owner.mv_spd -= self.slow_amount

        if self.paralyze:
            self.duration -= 1
            self.owner.paralyzed = True
