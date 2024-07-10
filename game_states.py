from enum import Enum


class GameStates(Enum):
    PLAYER_TURN = 1
    ENEMY_TURN = 2
    PLAYER_DEAD = 3
    TARGETING = 4
    MENU = 5


class NpcStates(Enum):
    IDLE = "idle"
    QUEST_INITIATED = "quest_initiated"
    QUEST_COMPLETED = "quest_completed"
    QUEST_FAILED = "quest_failed"
    HOSTILE = "hostile"
    SHOP = "shop"
