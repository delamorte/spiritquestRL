from components.AI.ai_basic import AIBasic


class AICaster(AIBasic):
    def __init__(self, ally=False):
        super().__init__(ally=ally)
        self.weights = {
            "heal_self": 5,
            "escape": 4,
            "ranged_attack": 3,
            "melee_attack": 3,
            "self_targeting": 2,
            "heal_buff_others": 2
        }

    def move_action(self, target, entities, game_map, target_range):
        if target_range:
            # Try to move closer
            self.owner.move_towards(target.x, target.y, game_map)
        else:
            # Move further
            self.owner.move_towards(target.x, target.y, game_map, escape=True)

