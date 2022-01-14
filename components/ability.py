class Ability:
    def __init__(self, name, description, skill_type, damage=None, dps=None, effect=None, duration=None,
                 radius=None, chance=None, rank=None, icon=None, needs_ai=None, target_self=None,
                 target_other=None, player_only=None, blt_input=None, power=None, requires_targeting=None,
                 targets_fighters_only=None, target_area=None, summoned_entities=None):
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
        self.blt_input = blt_input
        self.power = power
        self.requires_targeting = requires_targeting
        self.targets_fighters_only = targets_fighters_only
        self.target_area = target_area
        self.summoned_entities = summoned_entities

    def get_range(self):
        if self.radius:
            radius = self.radius[self.rank]
        else:
            radius = 1
        return radius
