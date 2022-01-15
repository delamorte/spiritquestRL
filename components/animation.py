import numpy as np


class Animation:
    def __init__(self, target, skill, frames=30, target_self=False):
        self.owner = None
        self.target = target
        self.skill = skill
        self.icon = None
        self.frames = frames
        self.target_self = target_self
        self.cached_arr = None

        if target_self:
            # Drawk skill usage animation on top of the entity
            self.offset_x = -10
            self.offset_y = -10
        else:
            # Draw skill usage animation to top left of entity tile
            self.offset_x = 1
            self.offset_y = 4
        self.icon = self.skill.icon
        self.color = self.get_color()

    def get_color(self):
        if self.skill.color:
            color = self.skill.color
        elif self.skill.skill_type == "weapon":
            color = "red"
        elif self.skill.skill_type == "utility":
            color = "amber"
        else:
            color = "amber"

        return color
