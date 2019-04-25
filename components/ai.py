from fov import recompute_fov
from random import randint

class BasicMonster:
    def __init__(self):
        self.action_begin = False
        self.last_action = 0
        self.target_seen = False
        self.target_last_seen_x = 0
        self.target_last_seen_y = 0

    def take_turn(self, target, fov_map, game_map, entities, time):
        monster = self.owner
        if not self.action_begin:
            self.last_action = time.get_last_turn()
        time_to_act = time.get_turn() - self.last_action
        action_cost = 0
        combat_msg = []
        recompute_fov(fov_map, monster.x, monster.y, monster.fighter.fov, True, 8)
        
        if fov_map.fov[target.y, target.x]:
            
            self.target_seen = True
            self.target_last_seen_x = target.x
            self.target_last_seen_y = target.y
            self.action_begin = True
            
            while action_cost < time_to_act: 

                if 1 / self.owner.fighter.mv_spd <= time_to_act - action_cost and monster.distance_to(target) >= 2:

                    monster.move_astar(target, entities, game_map)
                    action_cost += 1 / monster.fighter.mv_spd
                    #self.last_action += action_cost
                    self.action_begin = False

                elif self.owner.fighter.atk_spd <= time_to_act - action_cost: 
                    if target.fighter.hp > 0:
                        combat_msg = monster.fighter.attack(target)
                        action_cost += 1
                        #self.last_action += action_cost
                        self.action_begin = False
                    else:
                        break
                        
                else:
                    break

        elif self.target_seen:
            self.action_begin = False
            if not monster.x == self.target_last_seen_x and not monster.y == self.target_last_seen_y:
                monster.move_astar(target, entities, game_map)
            
        else:
            self.idle_actions(game_map)

        return combat_msg
    
    def idle_actions(self, game_map):
        
        dx = randint(-1, 1)
        dy = randint(-1, 1)
        dest_x = dx + self.owner.x
        dest_y = dy + self.owner.y
        
        if not game_map.is_blocked(dest_x, dest_y):
            
            self.owner.move(dx, dy)

            

        
    