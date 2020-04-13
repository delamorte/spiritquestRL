from map_objects.game_map import GameMap
from ui.menus import choose_avatar


def make_map(destination, levels, player, entities, game_map, stairs):
    # Set debug level
    if destination == "debug":
        entities = {}
        game_map = GameMap(100, 100, "debug")
        # game_map.generate_trees(0, 0, game_map.width,
        #                        game_map.height, 20, block_sight=True)
        # game_map.generate_forest()
        # game_map.generate_cavern()
        player, entities = game_map.place_entities(player, entities)
        # Initialize field of view
        player.light_source.initialize_fov(game_map)

    elif destination == "dream":
        choice, params = choose_avatar(player)
        if not choice:
            return game_map, entities, player
        if not params:
            return game_map, entities, player
        world_tendency = sum(params.values())
        game_map = GameMap(100, 100, "dream")
        # entities = game_map.generate_forest(world_tendency)
        entities = game_map.room_addition(world_tendency=world_tendency)
        player, entities = game_map.place_entities(player, entities, world_tendency)
        # Initialize field of view
        player.light_source.initialize_fov(game_map)
        player.fighter = player.player.avatar[choice]
        player.char = player.player.char[choice]

    elif destination == "cavern" + str(stairs.floor + 1):
        game_map = GameMap(100, 100, destination, stairs.floor + 1)
        entities = game_map.generate_cavern(entities)
        player, entities = game_map.place_entities(player, entities, stairs)
        # Initialize field of view
        player.light_source.initialize_fov(game_map)
        levels[game_map.name] = [game_map, entities]

    return game_map, entities, player


def level_change(destination, levels, player, entities=None, game_map=None, stairs=None):
    if not levels:
        game_map = GameMap(40, 40, "hub")
        entities = game_map.generate_hub()
        levels[game_map.name] = [game_map, entities]

    if destination in levels:
        game_map = levels[destination][0]
        entities = levels[destination][1]
        entities["player"] = [player]
        player, entities = game_map.place_entities(player, entities, stairs)
        player.light_source.initialize_fov(game_map)

        if destination == "hub":
            player.fighter = player.player.avatar["player"]
            player.char = player.player.char["player"]
            # player.color = None

    else:
        game_map, entities, player = make_map(destination, levels, player, entities, game_map, stairs)

    return game_map, entities, player
