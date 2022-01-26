class StatusEffects:
    def __init__(self, name):
        self.owner = None
        self.name = name
        self.items = []
        self.names = []

    def add_item(self, item):
        if item.description not in self.names:
            self.items.append(item)

    def remove_item(self, item):
        self.items.remove(item)

    def remove_all(self):
        self.items = []
        self.names = []

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
