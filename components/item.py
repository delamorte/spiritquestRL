from components.light_source import LightSource
from ui.message import Message

misc_decor = ["grass", "rubble", "rocks", "shrub", "bones"]
light_sources = ["candle", "lantern"]


class Item:
    def __init__(self, name, pickable=True, interactable=False):
        self.owner = None
        self.name = name
        self.pickable = pickable
        self.interactable = interactable

    def set_attributes(self, game_map):

        if self.name in light_sources:
            light_component = LightSource(name=self.name)
            self.owner.light_source = light_component
            self.owner.light_source.owner = self.owner
            self.owner.light_source.initialize_fov(game_map)
            self.owner.light_source.recompute_fov(self.owner.x, self.owner.y)

    def interaction(self, game_map):
        msg = None
        if self.name == "candle" and self.owner.light_source:
            msg = "You blow out the candle."
            self.owner.light_source = None

        elif self.name == "candle" and not self.owner.light_source:
            self.set_attributes(game_map)
            msg = "You light the candle."

        return Message(msg)
