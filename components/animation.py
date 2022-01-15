from math import ceil

import numpy as np


class Animation:
    def __init__(self, target, skill, num_of_frames=30, target_self=False):
        self.owner = None
        self.target = target
        self.skill = skill
        self.num_of_frames = num_of_frames
        self.target_self = target_self

        if target_self:
            # Drawk skill usage animation on top of the entity
            self.offset_x = -10
            self.offset_y = -10
        else:
            # Draw skill usage animation to top left of entity tile
            self.offset_x = 1
            self.offset_y = 4

        if skill.efx_icons:
            self.frames = [0xE800 + x for x in skill.efx_icons]
        else:
            print(str(skill.icon))
            self.frames = [skill.icon]

        half_split = int(self.num_of_frames / 2)
        a = np.linspace(20, 255, half_split, dtype=int)
        self.cached_alpha = np.concatenate((a, np.flip(a)))
        if len(self.frames) > 1 and len(self.frames) % 2 != 0:
            middle_idx = ceil(len(self.frames)/2)
            self.frames.insert(middle_idx, self.frames[middle_idx])
        self.cached_frames = np.repeat(self.frames, self.cached_alpha.size/len(self.frames))

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
