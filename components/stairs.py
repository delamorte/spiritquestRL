from components.light_source import LightSource


class Stairs:
    def __init__(self, source, destination, name=None, floor=None):
        """ 
        The constructor for Stairs class. 
  
        Parameters: 
           source (tuple): ("level name", x, y) 
           destination (list): ["destination level name", x, y]
           name (string): "stairs up" or "stairs down", can be left empty
           floor(int): current dungeon level   
        """
        self.owner = None
        self.name = name
        self.source = source
        self.destination = destination
        self.floor = floor

    def set_attributes(self, game_map):
        if self.name == "holy symbol":
            light_component = LightSource(name=self.name)
            self.owner.light_source = light_component
            self.owner.light_source.owner = self.owner
            self.owner.light_source.initialize_fov(game_map)
            self.owner.light_source.recompute_fov(self.owner.x, self.owner.y)
