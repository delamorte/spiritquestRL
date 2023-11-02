from ui.message import Message


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

    def interaction(self, levels):
        levels.change(self.destination[0])
        results = []
        if levels.current_map.name == "cavern" and levels.current_map.dungeon_level == 1:
            msg = Message(msg="A sense of impending doom fills you as you delve into the cavern.", clear_buffer=True)
            results.append(msg)
            msg2 = Message("RIBBIT!")
            results.append(msg2)

        elif levels.current_map.name == "dream":
            msg = Message(msg="I'm dreaming... I feel my spirit power draining.", clear_buffer=True)
            results.append(msg)
            msg2 = Message("I'm hungry..")
            results.append(msg2)

        return results
