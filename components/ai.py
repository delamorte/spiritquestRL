from fov import recompute_fov

class BasicMonster:
    def __init__(self):
        self.action_begin = False
        self.last_action = 0

    def take_turn(self, target, fov_map, game_map, entities, time):
        monster = self.owner
        if not self.action_begin:
            self.last_action = time.get_last_turn()
        time_to_act = time.get_turn() - self.last_action
        action_cost = 0
        combat_msg = []
        recompute_fov(fov_map, monster.x, monster.y, monster.fov)
        
        if fov_map.fov[target.y, target.x]:

            self.action_begin = True
            
            while action_cost < time_to_act: 

                if 1 / self.owner.fighter_c.mv_spd <= time_to_act - action_cost and monster.distance_to(target) >= 2:

                    monster.move_astar(target, entities, game_map)
                    action_cost += 1 / monster.fighter_c.mv_spd
                    #self.last_action += action_cost
                    self.action_begin = False

                elif self.owner.fighter_c.atk_spd <= time_to_act - action_cost: 
                    if target.fighter_c.hp > 0:
                        combat_msg = monster.fighter_c.attack(target)
                        action_cost += 1
                        #self.last_action += action_cost
                        self.action_begin = False
                        
                else:
                    self.last_action = time.get_last_turn()
                    break

        if action_cost > 0:
            time.take_turn(action_cost)
            return combat_msg
    