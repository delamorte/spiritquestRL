class Ability:
    def __init__(self, name, description, skill_type, damage=None, effect=None, duration=None,
                 radius=None, chance=None, rank=None, needs_ai=None, target_self=None):
        self.owner = None
        self.name = name
        self.description = description
        self.skill_type = skill_type
        self.damage = damage
        self.effect = effect
        self.duration = duration
        self.radius = radius
        self.chance = chance
        self.rank = rank
        self.needs_ai = needs_ai
        self.target_self = target_self
