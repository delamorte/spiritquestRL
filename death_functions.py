from game_states import GameStates
from helpers import get_article
from map_objects.tilemap import tilemap


def kill_player(player):
    player.char = tilemap()["player_remains"]
    return "[color=red]You died!", GameStates.PLAYER_DEAD


def kill_monster(monster):
    death_message = "The {0} is dead!".format(monster.name)
    if monster.boss:
        monster.char = tilemap()["boss_remains"]
        monster.color = "dark crimson"
    else:
        monster.char = tilemap()["monster_remains"]
        monster.color = "dark gray"
        monster.light_source = None
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = "remains of " + get_article(monster.name) + " " + monster.name
    monster.layer = 1

    return death_message
