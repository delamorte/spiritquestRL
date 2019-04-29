from random import randint
from map_objects.tilemap import abilities as abilities_db
from game_states import GameStates


class Fighter:
    def __init__(self, hp, ac, ev, power, mv_spd, atk_spd, size, fov=6, abilities=None):
        self.max_hp = hp
        self.hp = hp
        self.ac = ac
        self.ev = ev
        self.power = power
        self.mv_spd = mv_spd
        self.atk_spd = atk_spd
        self.fov = fov
        self.size = size
        self.abilities = abilities
        self.effects = []
        self.dead = False
        self.paralysis = False

    def take_damage(self, amount):
        results = []
        self.hp -= amount
        if self.hp <= 0:
            self.dead = True
        return results

    def attack(self, target, ability=None):
        results = []
        d = None
        hit_chance = randint(1, 100)
        damage = randint(1, self.power) - target.fighter.ac
        
        if ability in abilities_db()["attack"]:
            damage, effect = self.use_ability(ability, target)

            if len(effect) > 0:
                d = [effect, damage]
            if self.owner.player:
                results.append("You use {0} on {1}!".format(
                    ability, target.name))
            else:
                results.append("The {0} uses {1} on you!".format(
                    self.owner.name, ability))

        if target.fighter.ev * 5 >= hit_chance:
            if self.owner.player:
                results.append(
                    "You attack the {0}, but miss.".format(target.name))
            else:
                results.append(
                    "The {0} attacks you, but misses.".format(self.owner.name))

        elif damage > 0:
            if self.owner.player:
                results.append("You attack the {0} for {1} hit points.".format(
                    target.name, str(damage)))
                if d:
                    target.fighter.effects.append(d)
                    results.append("The {0} is inflicted with {1}!".format(target.name, d[0]))

            else:
                results.append("The {0} attacks you for {1} hit points.".format(
                    self.owner.name, str(damage)))
                
                if d:
                    target.fighter.effects.append(d)
                    results.append("You are inflicted with " + d[0] + "!")
                    
            results.extend(target.fighter.take_damage(damage))

        else:
            if self.owner.player:
                results.append(
                    "You attack the {0} but do no damage.".format(target.name))
            else:
                results.append(
                    "The {0} attacks you but does no damage.".format(self.owner.name))
        return results

    def use_ability(self, ability, target):

        effects = abilities_db()["attack"][ability]
        damage = randint(int(effects[1][0]), int(effects[1][2]))
        if ability == "swoop" and target.fighter.size == "small":
            damage += 2
        effect = effects[2]

        return damage, effect

    def process_effects(self, time_counter, game_state):
        results = []
        if len(self.effects) == 0:
            return results, game_state
        else:
            for x in self.effects:
                effect = x[0]
                duration = x[1]
                if duration == 0:
                    if effect == "paralyze":
                        self.paralysis = False
                    self.effects.remove(x)
                if effect == "poison":
                    self.take_damage(1)
                    x[1] -= 1
                if effect == "paralyze":
                    self.paralysis = True

                    time_counter.take_turn(1)
                    x[1] -= 2
                    
                    if x[1] <= 0:
                        self.paralysis = False
                    
                    if self.owner.player and self.paralysis:
                        results.append("You are paralyzed!")
                        game_state = GameStates.ENEMY_TURN
                    elif self.paralysis:
                        results.append("The {0} is paralyzed!".format(self.owner.name))
                        game_state = GameStates.PLAYER_TURN
                        
        return results, game_state
