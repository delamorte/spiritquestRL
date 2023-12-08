from enum import Enum


class GameStates(Enum):
    PLAYER_TURN = 1
    ENEMY_TURN = 2
    PLAYER_DEAD = 3
    TARGETING = 4
    MENU = 5
