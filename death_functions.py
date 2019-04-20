from game_states import GameStates


def kill_player(player):
    player.char = 0xE100 + 468
    return "[color=red]You died!", GameStates.PLAYER_DEAD


def kill_monster(monster):
    death_message = "{0} is dead!".format(monster.name.capitalize())

    monster.char = 0xE100 + 513
    monster.blocks = False
    monster.fighter = False
    monster.fighter_c = None
    monster.ai = False
    monster.ai_c = None
    monster.name = "Remains of " + monster.name

    return death_message
