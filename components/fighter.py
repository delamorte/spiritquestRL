class Fighter:
    def __init__(self, hp, ac, ev, power):
        self.max_hp = hp
        self.hp = hp
        self.ac = ac
        self.ev = ev
        self.power = power

    def take_damage(self, amount):
        results = []
        self.hp -= amount
        if self.hp <= 0:
            results.append(self.owner.name + " is dead.")
        return results

    def attack(self, target):
        results = []
        damage = self.power - target.fighter_c.ac

        if damage > 0:
            results.append('{0} attacks {1} for {2} hit points.'.format(
                self.owner.name.capitalize(), target.name, str(damage)))
            results.extend(target.fighter_c.take_damage(damage))
        else:
            results.append('{0} attacks {1} but does no damage.'.format(
                self.owner.name.capitalize(), target.name))
        return results