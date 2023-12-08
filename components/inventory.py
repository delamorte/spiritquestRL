from ui.message import Message


class Inventory:
    def __init__(self, capacity=20):
        self.owner = None
        self.capacity = capacity
        self.items = []
        
    def add_item(self, game_map, item=None):
        results = []

        if item:
            self.items.append(item)
            msg = Message("{0} was added to your inventory.".format(item.name))
            results.append(msg)
            return results

        entities = game_map.tiles[self.owner.x][self.owner.y].items_on_tile
        if entities:
            for entity in entities:
                if entity.item and entity.item.pickable and not entity.hidden:
                    if len(self.items) >= self.capacity:
                        msg = Message("Your inventory is full.")
                        results.append(msg)
                    else:
                        msg = Message("You pick up the {0}.".format(entity.name))
                        results.append(msg)
                        self.items.append(entity)
                        game_map.tiles[self.owner.x][self.owner.y].remove_entity(entity)
                        game_map.entities["items"].remove(entity)

        return results
