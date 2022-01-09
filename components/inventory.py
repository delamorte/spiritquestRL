class Inventory:
    def __init__(self, capacity):
        self.owner = None
        self.capacity = capacity
        self.items = []
        
    def add_item(self, game_map, msg_log, item=None):
        results = []
        entities = game_map.tiles[self.owner.x][self.owner.y].entities_on_tile
        if entities:
            for entity in entities:
                if entity.item and entity.item.pickable:
                    if len(self.items) >= self.capacity:
                        results.append("Your inventory is full.")
                    else:
                        results.append("You pick up the {0}.".format(entity.name))
                        self.items.append(entity)
                        game_map.tiles[self.owner.x][self.owner.y].remove_entity(entity)
                        game_map.entities["items"].remove(entity)

                    for msg in msg_log.stack:
                        if entity.name == msg.split(" ", 1)[1]:
                            msg_log.stack.remove(msg)

        return results
