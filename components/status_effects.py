class StatusEffects:
    def __init__(self, name):
        self.owner = None
        self.name = name
        self.items = []
        self.poison = None
        self.paralyze = None
        self.blind = None
        self.disease = None

    def add_item(self, item):
        if item.description not in self.owner.fighter.effects:
            self.items.append(item)

    def remove_item(self, item):
        self.items.remove(item)

    def process_effects(self):
        results = []

        for effect in self.items:
            processed_effect = effect.process()
            if processed_effect is not None:
                results.append(processed_effect)
        if results:
            for x in results:
                self.items.remove(x)
