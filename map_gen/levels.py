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
            level_choices = []
            for i in range(5):
                biome = Biome()
                level_choices.append(biome)
            level_data = MenuData(name="choose_level", params=level_choices)
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

    def make_debug_map(self, algorithm):
        biome = Biome(biome_modifier=self.world_tendency)
        game_map = GameMap(width=50,
                           height=50,
                           name="dream",
                           biome=biome,
                           title=algorithm)
        game_map.owner = self
        game_map.biome = biome
        game_map.generate_biome()
        game_map.generate_map(name=algorithm)
        return game_map

