from random import choice, random, choices

from data import json_data
from map_gen.tilemap import get_fighters_by_attribute


class Biome:
    def __init__(self, title=None, biome_type=None, biome_data=None, biome_prefix=None,
                 biome_suffix=None, biome_modifier=0, biome_monster=None,
                 biome_monster_chance=0.7, features=None, secrets=None,
                 npcs=None, quests=None, bosses=None, generate_random=True):
        self.title = title
        self.biome_type = biome_type
        self.biome_data = biome_data
        self.biome_prefix = biome_prefix
        self.biome_suffix = biome_suffix
        self.biome_modifier = biome_modifier
        self.biome_monster = biome_monster
        self.biome_monster_chance = biome_monster_chance
        self.home = None
        self.features = features
        self.secrets = secrets
        self.npcs = npcs
        self.quests = quests
        self.bosses = bosses
        self.generate_random = generate_random
        self.generate_biome_params(title)

    def generate_biome_params(self, title):

        # Set biome type and modifier
        self.set_biome_type(title)
        self.set_biome_features()
        if not title:
            self.set_biome_suffix_and_modifier()
            # Set level title, set dominant monster type
            if random() > self.biome_monster_chance:
                self.set_biome_monster()
                self.title = (
                            "The " + self.biome_prefix.capitalize() + " " + self.biome_monster.capitalize() + " " +
                            self.biome_type.capitalize() + " of " +
                            self.biome_suffix)
            else:
                self.title = "The " + self.biome_prefix.capitalize() + " " + self.biome_type.capitalize() + " of " + self.biome_suffix

    def set_biome_type(self, title=None):
        biomes_json = json_data.data.biomes
        if title and not self.generate_random:
            self.biome_data = biomes_json[title]
        else:
            biomes_list = list(biomes_json.values())
            biome_choices = [x for x in biomes_list if x["biome_type"] != "prefab"]
            self.biome_data = choice(biome_choices)
        self.biome_type = self.biome_data["biome_type"]
        self.biome_prefix = choice(self.biome_data["prefixes"])

    def set_biome_features(self):
        if self.biome_data["features"]:
            self.features = self.biome_data["features"]
        if self.biome_data["quests"]:
            self.quests = choice(self.biome_data["quests"])
        if self.biome_data["npcs"]:
            self.npcs = choice(self.biome_data["npcs"])
        if self.biome_data["bosses"]:
            self.bosses = choice(self.biome_data["bosses"])

    def set_biome_suffix_and_modifier(self):
        # negative integers represents chaos. positive ints harmony,
        # zero is neutrality.
        params = {"Death and Decay": -3,
                  "the Red Sun": -1,
                  "Pain, Suffering and Misery": -1,
                  "Winds of Ice": 0,
                  "Solitude": 2,
                  "the Mother Moon": 2,
                  "a Love that Never Dies": 3,
                  "Summer Skies of Love": 1,
                  "Happiness": +1,
                  "Sorrow": -1,
                  "Deadly Petals with Strange Power": -1,
                  "the Numbing Chill": 0,
                  "the Day of Judgement": 0,
                  "the Sapphire Haze": 1,
                  "Plastic Flowers and Melting Sun": -1,
                  "the Golden Chorus": 3
                  }
        title, biome_mod = choice(list(params.items()))
        self.biome_suffix = title
        self.biome_modifier += biome_mod

    def set_biome_monster(self):
        if self.biome_modifier < 0:
            monsters = get_fighters_by_attribute("chaos", True)
        elif self.biome_modifier > 0:
            monsters = get_fighters_by_attribute("light", True)
        else:
            monsters = get_fighters_by_attribute("neutral", True)
        monsters.sort()
        spawn_rates = get_spawn_rates(monsters)
        monster_prefix = choice(choices(monsters, spawn_rates, k=5))[0]
        self.biome_monster = monster_prefix


def get_spawn_rates(monsters):
    rates = {"rat": 0.2,
             "crow": 0.2,
             "snake": 0.2,
             "frog": 0.15,
             "bear": 0.10,
             "felid": 0.20,
             "mosquito": 0.10,
             "chaos cat": 0.05,
             "chaos bear": 0.03,
             "cockroach": 0.20,
             "bone snake": 0.10,
             "chaos dog": 0.15,
             "bat": 0.2,
             "imp": 0.15,
             "leech": 0.15,
             "spirit": 0.15,
             "chaos spirit": 0.10,
             "ghost dog": 0.15,
             "gecko": 0.10,
             "serpent": 0.05,
             "fairy": 0.07}

    spawn_rates = []
    for mon in monsters:
        spawn_rates.append(rates[mon[0]])

    return spawn_rates
