import random

from fighter_stats import get_spawn_rates
from map_objects.game_map import GameMap
from map_objects.tilemap import tilemap
from descriptions import level_biomes, meditate_params
from draw import draw_side_panel_content
from ui.menus import choose_mission
import variables


def make_map(destination, levels, player, entities, game_map, stairs):

    # Set debug level
    if destination == "debug":
        entities = {}
        game_map = GameMap(20, 20, "debug")
        # game_map.generate_trees(0, 0, game_map.width,
        #                        game_map.height, 20, block_sight=True)
        # game_map.generate_forest()
        # game_map.generate_cavern()
        player, entities = game_map.place_entities(player, entities)
        # Initialize field of view
        player.light_source.initialize_fov(game_map)

    elif destination == "dream":
        level_params = generate_level_params()
        level_choice = choose_mission(level_params)
        if not level_choice:
            game_map.tiles[player.x][player.y].entities_on_tile.append(player)
            return game_map, entities, player
        variables.world_tendency = level_choice["modifier"]
        game_map = GameMap(100, 100, "dream")
        # entities = game_map.generate_forest(world_tendency)
        entities = game_map.room_addition()
        player, entities = game_map.place_entities(player, entities)
        # Initialize field of view
        player.light_source.initialize_fov(game_map)
        player.light_source.radius = player.fighter.fov
        player.light_source.recompute_fov(player.x, player.y)

    elif destination == "cavern" + str(stairs.floor + 1):
        game_map = GameMap(20, 20, "debug")
        entities = game_map.generate_cavern(entities)
        player, entities = game_map.place_entities(player, entities)
        # Initialize field of view
        player.light_source.initialize_fov(game_map)
        levels[game_map.name] = [game_map, entities]

    return game_map, entities, player


def generate_level_params(level_params=None):

    if level_params is None:
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
            if variables.world_tendency < 0:
                for x, y in tilemap()["monsters_chaos"].items():
                    monsters.append((x, y))
            elif variables.world_tendency > 0:
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


def level_change(destination, levels, player, entities=None, game_map=None, stairs=None, ui_elements=None):

    if not levels:
        game_map = GameMap(40, 40, "hub")
        entities = game_map.generate_hub()
        levels[game_map.name] = [game_map, entities]

    if destination in levels:
        game_map = levels[destination][0]
        entities = levels[destination][1]
        entities["player"] = [player]
        player, entities = game_map.place_entities(player, entities, stairs)
        player.fighter = player.player.avatar["player"]
        player.light_source.initialize_fov(game_map)
        player.light_source.radius = player.fighter.fov
        player.light_source.recompute_fov(player.x, player.y)

        if destination == "hub":
            player.fighter = player.player.avatar["player"]
            player.char = player.player.char["player"]
            # player.color = None

    else:
        game_map, entities, player = make_map(destination, levels, player, entities, game_map, stairs)

    draw_side_panel_content(game_map, player, ui_elements)
    return game_map, entities, player
