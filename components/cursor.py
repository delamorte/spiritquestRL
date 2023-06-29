from ui.message import Message


class Cursor:
    def __init__(self, targeting_ability=None):
        self.owner = None
        self.targeting_ability = targeting_ability
        self.sel_index = 0
        self.sel_max_index = 0

    def select_next(self, entities, game_map):
        self.sel_max_index = len(entities)
        if self.sel_index + 1 < self.sel_max_index:
            self.sel_index += 1
        else:
            self.sel_index = 0
        next_entity = entities[self.sel_index]
        game_map[self.owner.x][self.owner.y].remove_entity(self.owner)
        self.owner.x, self.owner.y = next_entity.x, next_entity.y
        game_map[self.owner.x][self.owner.y].add_entity(self.owner)

        if game_map[self.owner.x][self.owner.y].name is not None:
            return Message(game_map[self.owner.x][self.owner.y].name.capitalize())
