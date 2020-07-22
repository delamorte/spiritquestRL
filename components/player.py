from map_objects.tilemap import tilemap
import numpy as np


class Player:
    def __init__(self, spirit_power):
        self.owner = None
        self.spirit_power = spirit_power
        self.char = {"player": tilemap()["player"]}
        self.char_exp = {"player": 0}
        self.avatar = {"player": None}
        self.lightmap = None

    def init_light(self):
        self.lightmap = np.ones_like(self.owner.light_source.fov_map.fov, dtype=float)


    def calculate_light(self):
        pass