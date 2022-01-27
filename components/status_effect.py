from math import ceil
from random import random


class StatusEffect:
    def __init__(self, owner, source, name, description=None, dps=None, delayed_damage=None, rank=None,
                 fly=None, sneak=None, reveal=None, invisibility=None, slow=None, drain_stats=None,
                 hit_penalty=None, paralyze=None, duration=None, chance=None, color=None, power=None,
                 heal=None, summon=None, target_self=None, drain_atk=None, boost_atk=None,
                 boost_ac=None, boost_hp=None, boost_ev=None):
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
        self.inv_ev_boost = 0
        self.rank = rank
        self.color = color
        self.drain_stats = drain_stats
        self.drain_atk = drain_atk
        self.boost_atk = boost_atk
        self.boost_ac = boost_ac
        self.boost_hp = boost_hp
        self.boost_ev = boost_ev
        self.hit_penalty = hit_penalty
        self.paralyze = paralyze
        self.duration = duration
        self.chance = chance
        self.power = power
        self.heal = heal
        self.summon = summon
        self.target_self = target_self
        self.slow_amount = None
        self.process_instantly = False

        # Process buffs etc. instantly after casting
        if self.fly or self.heal or self.reveal or self.invisibility or self.sneak or self.summon:
            self.process_instantly = True

    def process(self, game_map=None, fighter=None):
        msg = None

        if self.process_instantly:
            self.process_instantly = False

        if self.source.owner.dead and self.name == "strangle":
            self.duration = 0

        if self.heal:
            msg = fighter.heal(self.power[self.rank])
            return self, msg

        if self.duration <= 0:

            if self.hit_penalty:
                fighter.hit_penalty -= self.hit_penalty[self.rank]
            if self.drain_stats:
                fighter.ac += self.power[self.rank]
                fighter.ev += self.power[self.rank]
            if self.drain_atk:
                fighter.atk += self.power[self.rank]
            if self.boost_atk:
                fighter.atk -= self.power[self.rank]
            if self.boost_ac:
                fighter.ac -= self.power[self.rank]
            if self.boost_hp:
                fighter.hp -= self.power[self.rank]
            if self.boost_ev:
                fighter.ev -= self.power[self.rank]
            if self.slow_amount:
                fighter.mv_spd += self.slow_amount
            if self.delayed_damage:
                fighter.take_damage(self.delayed_damage)
            if self.fly:
                fighter.ev -= self.fly_ev_boost
            if self.invisibility:
                fighter.ev -= self.inv_ev_boost
            return self, msg

        if self.dps:
            fighter.take_damage(self.dps[self.rank])

        if self.hit_penalty:
            if not self.owner.has_effect(self.description):
                fighter.hit_penalty += self.hit_penalty[self.rank]

        if self.drain_stats:
            if not self.owner.has_effect(self.description):
                fighter.hit_penalty -= self.power[self.rank]
                fighter.ac -= self.power[self.rank]
                fighter.ev -= self.power[self.rank]

        if self.drain_atk:
            if not self.owner.has_effect(self.description):
                fighter.atk -= self.power[self.rank]

        if self.boost_atk:
            if not self.owner.has_effect(self.description):
                fighter.atk += self.power[self.rank]
        
        if self.boost_ac:
            if not self.owner.has_effect(self.description):
                fighter.ac += self.power[self.rank]

        if self.boost_hp:
            if not self.owner.has_effect(self.description):
                fighter.hp += self.power[self.rank]

        if self.boost_ev:
            if not self.owner.has_effect(self.description):
                fighter.ev += self.power[self.rank]

        if self.slow:
            if not self.owner.has_effect(self.description):
                self.slow_amount = fighter.mv_spd - fighter.mv_spd * self.slow[self.rank]
                fighter.mv_spd -= self.slow_amount

        if self.fly:
            if not self.owner.has_effect(self.description):
                self.fly_ev_boost = ceil(fighter.ev * self.power[self.rank] - fighter.ev)
                fighter.ev += self.fly_ev_boost

        if self.reveal:
            neighbours = game_map.get_neighbours(fighter.owner, include_self=False,
                                                 fighters=False, mark_area=True,
                                                 radius=self.reveal.radius[self.rank], algorithm="square")
            for entity in neighbours:
                if entity.hidden:
                    entity.hidden = False

        if self.invisibility:
            if not self.owner.has_effect(self.description):
                self.inv_ev_boost = ceil(fighter.ev * ceil(1 + self.power[self.rank]) - fighter.ev)
                fighter.ev += self.inv_ev_boost
                
                if fighter.owner.player:
                    neighbours = game_map.get_neighbours(fighter.owner, include_self=False,
                                                         fighters=False, mark_area=True,
                                                         radius=fighter.fov, algorithm="disc")
                    for entity in neighbours:
                        if entity.ai:
                            if entity.ai.cant_see_player:
                                # If player has already passed the initial sneak check, have a constant chance of
                                # passing again
                                if random() > 0.66:
                                    entity.ai.cant_see_player = False
                            elif random() <= self.power[self.rank]:
                                # Initial sneak check
                                entity.ai.cant_see_player = True
                            else:
                                entity.ai.cant_see_player = False

        if self.sneak and fighter.owner.player:
            neighbours = game_map.get_neighbours(fighter.owner, include_self=False,
                                                 fighters=False, mark_area=True,
                                                 radius=self.sneak.radius[self.rank], algorithm="square")

            for entity in neighbours:
                if entity.ai:
                    if entity.ai.cant_see_player:
                        # If player has already passed the initial sneak check, have a constant chance of passing
                        # again
                        if random() > 0.66:
                            entity.ai.cant_see_player = False
                    elif random() <= self.power[self.rank]:
                        # Initial sneak check
                        entity.ai.cant_see_player = True
                    else:
                        entity.ai.cant_see_player = False

        self.duration -= 1

        return None, msg
