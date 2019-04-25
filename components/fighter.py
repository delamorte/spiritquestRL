from random import randint


class Fighter:
    def __init__(self, hp, ac, ev, power, mv_spd, atk_spd, fov=6):
        self.max_hp = hp
        self.hp = hp
        self.ac = ac
        self.ev = ev
        self.power = power
        self.mv_spd = mv_spd
        self.atk_spd = atk_spd
        self.fov = fov
        self.dead = False

    def take_damage(self, amount):
        results = []
        self.hp -= amount
        if self.hp <= 0:
            self.dead = True
        return results

    def attack(self, target):
        results = []
        hit_chance = randint(1, 100)
        damage = randint(1,self.power) - target.fighter.ac
        if target.fighter.ev * 5 >= hit_chance:
            if self.owner.player:
                results.append(
                    "You attack the {0}, but miss.".format(target.name))
            else:
                results.append("The {0} attacks you, but misses.".format(self.owner.name))

        elif damage > 0:
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
                    "You attack the {0} but do no damage.".format(target.name))
            else:
                results.append("The {0} attacks you but does no damage.".format(self.owner.name))
        return results

