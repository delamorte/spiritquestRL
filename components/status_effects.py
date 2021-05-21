class StatusEffects:
    def __init__(self, name):
        self.owner = None
        self.name = name
        self.items = []
        self.poison = None
        self.paralysis = None
        self.blind = None
        self.disease = None

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item):
        self.items.remove(item)

    def process_effects(self):
        results = []

        for effect in self.items:
            results.append(effect.process())
        for x in results:
            self.items.remove(x)
