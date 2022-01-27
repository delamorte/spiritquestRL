class StatusEffects:
    def __init__(self, name):
        self.owner = None
        self.name = name
        self.items = []

    def add_item(self, item):

        if not self.has_effect(item.description):
            self.items.append(item)

    def remove_item(self, item):
        self.items.remove(item)

    def remove_all(self):
        self.items = []

    def get_item(self, description):
        has_effect = next((x for x in self.items if x.description == description), False)
        return has_effect

    def has_effect(self, description):
        has_effect = next((True for x in self.items if x.description == description), False)
        return has_effect

    def process_effects(self, effect=None, game_map=None, self_targeting=False):
        results = []
        msgs = []
        fighter = self.owner.fighter

        if effect:
            processed_effect, msg = effect.process(game_map=game_map, fighter=fighter)
            if processed_effect is not None:
                self.items.remove(processed_effect)
            if msg:
                msgs.append(msg)
                return msgs
        elif self_targeting:
            for effect in self.items:
                if effect.process_instantly:
                    processed_effect, msg = effect.process(game_map=game_map, fighter=fighter)
                    if processed_effect is not None:
                        results.append(processed_effect)
                    if msg:
                        msgs.append(msg)
            if results:
                for x in results:
                    self.items.remove(x)
            if msgs:
                return msgs
        else:
            for effect in self.items:
                processed_effect, msg = effect.process(game_map=game_map, fighter=fighter)
                if processed_effect is not None:
                    results.append(processed_effect)
                if msg:
                    msgs.append(msg)
            if results:
                for x in results:
                    self.items.remove(x)
            if msgs:
                return msgs
