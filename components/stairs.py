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

    def interaction(self, levels, msg_log):
        levels.change(self.destination[0])
        msg_log.old_stack = msg_log.stack

        if levels.current_map.name == "cavern" and levels.current_map.dungeon_level == 1:
            msg_log.clear()
            msg_log.send(
                "A sense of impending doom fills you as you delve into the cavern.")
            msg_log.send("RIBBIT!")

        elif levels.current_map.name == "dream":
            msg_log.clear()
            msg_log.send("I'm dreaming... I feel my spirit power draining.")
            msg_log.send("I'm hungry..")
