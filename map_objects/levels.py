from fov import initialize_fov
from map_objects.game_map import GameMap
from ui.menus import choose_avatar

def level_change(level_name, levels, player, game_map=None, fov_map=None, depth=None,):

    entities=[]
    if not levels:
        game_map = GameMap(40, 40, "hub")
        entities = game_map.generate_hub(entities)
        levels.append(game_map)

    if level_name is "hub":
        for level in levels:
            if level.name is level_name:
                game_map = level
        # Initialize entities
        player, entities = game_map.place_entities(player, entities)
        # Initialize field of view
        fov_map = initialize_fov(game_map)
        player.fighter = player.player.avatar["player"]
        player.char = player.player.char["player"]

    if level_name is "dream":
        choice = choose_avatar(player)
        if not choice:
            return game_map, entities, player, fov_map
        game_map = GameMap(100, 100, "dream")
        game_map.generate_forest(entities)
        player, entities = game_map.place_entities(player, entities)
        # Initialize field of view
        fov_map = initialize_fov(game_map)
        player.fighter = player.player.avatar[choice]
        player.char = player.player.char[choice]

    if level_name is "cavern":
        for level in levels:
            if level.name is level_name and level.dungeon_level == depth:
                game_map = level
        game_map = GameMap(100, 100, "cavern", depth)
        game_map.generate_cavern(entities)
        player, entities = game_map.place_entities(player, entities)
        # Initialize field of view
        fov_map = initialize_fov(game_map)
        levels.append(game_map)

    # Set debug level
    if level_name is "debug":
        game_map = GameMap(30, 30, "debug")
        # game_map.generate_trees(0, 0, game_map.width,
        #                        game_map.height, 20, block_sight=True)
        # game_map.generate_forest()
        # game_map.generate_cavern()
        player, entities = game_map.place_entities(player, entities)
        # Initialize field of view
        fov_map = initialize_fov(game_map)

    return game_map, entities, player, fov_map
