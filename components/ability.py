from data import json_data


class Ability:
    def __init__(self, name, description, skill_type, owner=None, damage=None, dps=None, effect=None, duration=None,
                 radius=None, chance=None, rank=None, icon=None, needs_ai=None, target_self=None,
                 target_other=None, player_only=None, blt_input=None, power=None, requires_targeting=None,
                 targets_fighters_only=None, target_area=None, summoned_entities=None, color=None,
                 efx_icons=None, max_rank=2):
        self.owner = owner
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
        self.max_rank = max_rank
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
        self.color = color
        self.efx_icons = efx_icons

    def get_range(self):
        if self.radius:
            radius = self.radius[self.rank]
        else:
            radius = 1
        return radius

    def get_description(self, rank=None):
        item = json_data.data.abilities[self.name]
        if not rank:
            rank = self.rank
        player = self.owner
        skill_str = ""
        chance_str, atk_str, effect_str, duration_str = "", "", "", ""
        # if self.chance:
        #     # chance_str = str(int(1 / atk.chance[atk.rank])) + "% chance of "
        #     chance_str = "100% chance of "
        # if self.effect:
        #     effect_str = ", ".join(self.effect) + ", "
        if self.duration:
            duration_str = "{0} turns".format(item["duration"][min(len(item["duration"])-1, rank)])
        if self.damage:
            atk_str = ", " + item["damage"][min(len(item["damage"])-1, rank)] + "+" + str(player.fighter.str_bonus) + \
                      " dmg" if duration_str \
                else item["damage"][min(len(item["damage"])-1, rank)] + "+" + str(player.fighter.str_bonus) + " dmg"
        skill_str += chance_str + effect_str + duration_str + atk_str
        if self.radius:
            if skill_str:
                skill_str += ", radius: {0}".format(item["radius"][min(len(item["radius"])-1, rank)])
            else:
                skill_str += "radius: {0}".format(item["radius"][min(len(item["radius"]) - 1, rank)])

        return skill_str

    def rank_up(self):
        self.rank += 1
        if self.rank > self.max_rank:
            self.rank = self.max_rank
