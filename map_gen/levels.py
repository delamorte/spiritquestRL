import numpy as np

import options
from map_gen.biome import Biome
from map_gen.game_map import GameMap
from ui.menus import MenuData


class Levels:
    def __init__(self):
        self.owner = None
        self.tileset = options.data.gfx
        self.player = None
        self.items = {}
        self.params = None
        self.world_tendency = 0
        self.current_map = None

    def change(self, destination=None):
        # Clear animation buffer on level change
        self.owner.animations_buffer = []
        self.player = self.owner.player
        # Clear status effects on level change
        if self.player.status_effects.has_effect("summoning"):
            self.player.summoner.end_summoning(self.current_map)
        self.player.status_effects.remove_all()

        if not self.items:
            game_map = self.create_biome_and_map(name="hub", biome_title="hub", width=40, height=40, generate_random=False)
            self.items[game_map.name] = game_map
            self.current_map = game_map

        if destination in self.items:
            game_map = self.items[destination]
            #game_map.place_entities()
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

            # Initialize field of view
            self.player.light_source.initialize_fov(game_map)

        elif destination == "dream":
            level_choices = []
            for i in range(5):
                biome = Biome()
                level_choices.append(biome)
            level_data = MenuData(name="choose_level", params=level_choices)
            self.owner.menus.create_or_show_menu(level_data)
            if not self.owner.menus.choose_level.event:
                return
            self.world_tendency = self.params.biome_modifier

            game_map = self.create_biome_and_map(name="dream", biome_title=self.params.title, width=70, height=70)
            self.items[game_map.name] = game_map
            self.current_map = game_map

            # Initialize field of view
            self.current_map.recompute_fov(self.player)

    def make_debug_map(self, algorithm):
        if algorithm == "hub":
            game_map = self.create_biome_and_map(name="debug", biome_title="hub", width=70, height=70,
                                                 generate_random=False)
        else:
            game_map = self.create_biome_and_map(name="debug", width=70, height=70, algorithm=algorithm)
        return game_map

    def create_biome_and_map(self, name, width, height, biome_title=None, algorithm=None, generate_random=True):
        biome = Biome(biome_modifier=self.world_tendency, title=biome_title, generate_random=generate_random)
        game_map = GameMap(width=width,
                           height=height,
                           name=name,
                           biome=biome)
        game_map.owner = self
        game_map.biome = biome
        game_map.generate_map(name=algorithm)
        game_map.process_rooms()
        game_map.process_prefabs()
        if not self.owner.debug:
            game_map.place_player()
            game_map.init_light_sources()
        transparency = np.frompyfunc(lambda tile: not tile.block_sight, 1, 1)
        game_map.transparent = transparency(game_map.tiles)
        return game_map
