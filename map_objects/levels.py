import random

from map_objects.game_map import GameMap
from map_objects.tilemap import tilemap
from descriptions import level_biomes, meditate_params
from ui.menus import MenuData


class Levels:
    def __init__(self, tileset):
        self.owner = None
        self.tileset = tileset
        self.player = None
        self.items = {}
        self.params = None
        self.world_tendency = 0
        self.current_map = None

    def change(self, destination=None):

        self.player = self.owner.player
        # Clear status effects on level change
        if self.player.fighter.summoning:
            self.player.summoner.end_summoning(self.current_map)
        self.player.status_effects.remove_all()

        if not self.items:
            game_map = GameMap(40, 40, "hub")
            game_map.owner = self
            game_map.generate_hub()
            self.items[game_map.name] = game_map
            self.current_map = game_map

        if destination in self.items:
            game_map = self.items[destination]
            game_map.place_entities()
            self.current_map = game_map
            self.player.fighter = self.player.player.avatar["player"]
            self.current_map.recompute_fov(self.player)

            if destination == "hub":
                self.player.fighter = self.player.player.avatar["player"]
                self.player.char = self.player.player.char["player"]
                # player.color = None

        else:
            self.make_map(destination)

        self.owner.ui.side_panel.draw_content()

    def make_map(self, destination):

        # Set debug level
        if destination == "debug":
            game_map = GameMap(20, 20, "debug")
            game_map.owner = self
            # game_map.generate_trees(0, 0, game_map.width,
            #                        game_map.height, 20, block_sight=True)
            # game_map.generate_forest()
            # game_map.generate_cavern()
            game_map.place_entities()
            # Initialize field of view
            self.player.light_source.initialize_fov(game_map)

        elif destination == "dream":
            level_params = self.generate_level_params()
            level_data = MenuData(name="choose_level", params=level_params)
            self.owner.menus.create_or_show_menu(level_data)
            if not self.owner.menus.choose_level.event:
                return
            self.world_tendency = self.params["modifier"]
            game_map = GameMap(width=50,
                               height=50,
                               name="dream",
                               title=self.params["title"])
            game_map.owner = self
            game_map.generate_map()
            self.items[game_map.name] = game_map
            self.current_map = game_map
            game_map.place_entities()
            # Initialize field of view
            self.current_map.recompute_fov(self.player)

    def generate_level_params(self):

        level_params = []
        biomes = level_biomes()
        biome_params = meditate_params()
        for i in range(5):
            level = {}
            biome = random.choice(biomes)
            biome_desc, biome_mod = random.choice(list(biome_params.items()))
            level["biome"] = biome
            level["modifier"] = biome_mod
            level["freq_monster"] = None
            # Generate level title
            if random.random() > 0.7:
                monsters = []
                if self.world_tendency < 0:
                    for x, y in tilemap()["monsters_chaos"].items():
                        monsters.append((x, y))
                elif self.world_tendency > 0:
                    for x, y in tilemap()["monsters_light"].items():
                        monsters.append((x, y))
                else:
                    for x, y in tilemap()["monsters"].items():
                        monsters.append((x, y))
                monsters.sort()
                spawn_rates = self.get_spawn_rates(monsters)
                monster_prefix = random.choice(random.choices(monsters, spawn_rates, k=5))[0]
                level["title"] = "The " + monster_prefix.capitalize() + " " + biome.capitalize() + " of " + biome_desc
                level["freq_monster"] = monster_prefix
            else:
                level["title"] = "The " + biome.capitalize() + " of " + biome_desc
            level_params.append(level)

        return level_params

    def get_spawn_rates(self, monsters):
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
