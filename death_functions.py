from game_states import GameStates
from map_objects.tilemap import tilemap


def kill_player(player):
    player.char = tilemap()["player_remains"]
    return "[color=red]You died!", GameStates.PLAYER_DEAD


def kill_monster(monster):
    death_message = "{0} is dead!".format(monster.name.capitalize())

    monster.char = tilemap()["monster_remains"]
    monster.blocks = False
    monster.fighter = False
    monster.fighter_c = None
    monster.ai = False
    monster.ai_c = None
    monster.name = "Remains of " + monster.name
    monster.layer = 49

    return death_message
