from game_states import GameStates
from helpers import get_article
from map_objects.tilemap import tilemap



def kill_player(player):
    player.char = tilemap()["player_remains"]
    return "[color=red]You died!", GameStates.PLAYER_DEAD


def kill_monster(monster):
    death_message = "The {0} is dead!".format(monster.name)

    monster.char = tilemap()["monster_remains"]
    monster.blocks = False
    monster.fighter = False
    monster.fighter_c = None
    monster.ai = False
    monster.ai_c = None
    monster.name = "the remains of " + get_article(monster.name)+ " " + monster.name
    monster.layer = 11

    return death_message