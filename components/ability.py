class Ability:
    def __init__(self, name, description, skill_type, damage=None, dps=None, effect=None, duration=None,
                 radius=None, chance=None, rank=None, icon=None, needs_ai=None, target_self=None,
                 target_other=None, player_only=None):
        self.owner = None
        self.name = name
        self.description = description
        self.skill_type = skill_type
        self.damage = damage
        self.dps = dps
        self.effect = effect
        self.duration = duration
        self.radius = radius
        self.chance = chance
        self.rank = rank
        self.icon = 0xF100 + icon
        self.needs_ai = needs_ai
        self.target_self = target_self
        self.target_other = target_other
        self.player_only = player_only

