from enum import Enum, auto


class GameStates(Enum):
    PLAYER_TURN = auto()
    ENEMY_TURN = auto()
    ALLY_TURN = auto()
    PLAYER_DEAD = auto()
    TARGETING = auto()
    MENU = auto()
