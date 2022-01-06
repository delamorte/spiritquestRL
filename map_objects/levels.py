import random

from fighter_stats import get_spawn_rates
from map_objects.game_map import GameMap
from map_objects.tilemap import tilemap
from descriptions import level_biomes, meditate_params
import settings
from ui.menus import Menus, MenuData


class Levels:
    def __init__(self):
        self.owner = None
        self.player = None
        self.items = {}
        self.params = None
        self.world_tendency = 0
        self.current_map = None

    def change(self, destination=None):

        self.player = self.owner.player

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
            self.player.light_source.initialize_fov(game_map)
            self.player.light_source.radius = self.player.fighter.fov
            self.player.light_source.recompute_fov(self.player.x, self.player.y)

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
            self.player.light_source.initialize_fov(game_map)
            self.player.light_source.radius = self.player.fighter.fov
            self.player.light_source.recompute_fov(self.player.x, self.player.y)

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
                spawn_rates = get_spawn_rates(monsters)
                monster_prefix = random.choice(random.choices(monsters, spawn_rates, k=5))[0]
                level["title"] = "The " + monster_prefix.capitalize() + " " + biome.capitalize() + " of " + biome_desc
                level["freq_monster"] = monster_prefix
            else:
                level["title"] = "The " + biome.capitalize() + " of " + biome_desc
            level_params.append(level)

        return level_params
