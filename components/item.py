from components.light_source import LightSource
from ui.message import Message


class Item:
    def __init__(self, name, pickable=True, interactable=False, light_source=False):
        self.owner = None
        self.name = name
        self.pickable = pickable
        self.interactable = interactable
        self.light_source = light_source

    def set_attributes(self, game_map):

        if self.light_source:
            light_component = LightSource(name=self.name, light_walls=False)
            self.owner.light_source = light_component
            self.owner.light_source.owner = self.owner
            self.owner.light_source.initialize_fov(game_map)
            #self.owner.light_source.recompute_fov(game_map)

    def interaction(self, game_map):
        results = []
        if self.light_source and self.owner.light_source:
            msg = Message(msg="You put out the {0}.".format(self.name))
            results.append(msg)
            self.owner.light_source = None

        elif self.light_source and not self.owner.light_source:
            self.set_attributes(game_map)
            msg = Message(msg="You light the {0}.".format(self.name))
            results.append(msg)

        return results
