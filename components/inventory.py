class Inventory:
    def __init__(self, capacity):
        self.capacity = capacity
        self.items = []
        
    def add_item(self, item):
        results = []
        
        if len(self.items) >= self.capacity:
            results.append("Your inventory is full.")
            
        else:
            results.append("You pick up the {0}.".format(item.name))
            self.items.append(item)
            
        return results