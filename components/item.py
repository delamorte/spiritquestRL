misc_decor = ["grass", "rubble", "rocks", "shrub", "bones"]


class Item:
    def __init__(self, name, pickable=True):
        self.name = name
        self.pickable = pickable
