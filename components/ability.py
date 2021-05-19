class Ability:
    def __init__(self, name, description, skill_type, damage=None, effect=None, radius=None, chance=None):
        self.owner = None
        self.name = name
        self.description = description
        self.skill_type = skill_type
        self.damage = damage
        self.effect = effect
        self.radius = radius
        self.chance = chance
