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
        self.name = name
        self.source = source
        self.destination = destination
        self.floor = floor