class Fighter:
    def __init__(self, hp, ac, ev, power):
        self.max_hp = hp
        self.hp = hp
        self.ac = ac
        self.ev = ev
        self.power = power
        self.dead = False

    def take_damage(self, amount):
        results = []
        self.hp -= amount
        if self.hp <= 0:
            self.dead = True
        return results

    def attack(self, target):
        results = []
        damage = self.power - target.fighter_c.ac

        if damage > 0:
            if self.owner.player:
                results.append("You attack {0} for {1} hit points.".format(
                    target.name, str(damage)))
            else:
                results.append("{0} attacks you for {1} hit points.".format(
                    self.owner.name.capitalize(), str(damage)))
            results.extend(target.fighter_c.take_damage(damage))
        else:
            if self.owner.player:
                results.append(
                    "You attack {0} but do no damage.".format(target.name))
            else:
                results.append("{0} attacks you but does no damage.".format(
                    self.owner.name.capitalize()))
        return results
