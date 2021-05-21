from random import choices, randint


class BasicMonster:
    def __init__(self):
        self.owner = None
        self.action_begin = False
        self.last_action = 0
        self.target_seen = False
        self.target_last_seen_x = 0
        self.target_last_seen_y = 0

    def take_turn(self, target, game_map, entities, time):
        monster = self.owner
        if not self.action_begin:
            self.last_action = time.get_last_turn()
        time_to_act = time.get_turn() - self.last_action
        action_cost = 0
        combat_msg = []
        self.owner.light_source.recompute_fov(monster.x, monster.y)

        if self.owner.light_source.fov_map.fov[target.y, target.x]:
            
            self.target_seen = True
            self.target_last_seen_x = target.x
            self.target_last_seen_y = target.y
            self.action_begin = True
            
            while action_cost < time_to_act: 

                if monster.distance_to(target) == 1 and self.owner.fighter.atk_spd <= time_to_act - action_cost: 
                    if target.fighter.hp > 0:
                        combat_msg, skill = self.choose_skill()
                        if skill is None:
                            return combat_msg
                        combat_msg = monster.fighter.attack(target, skill)
                        action_cost += 1
                        #self.last_action += action_cost

                    else:
                        break
                    
                elif 1 / self.owner.fighter.mv_spd <= time_to_act - action_cost and monster.distance_to(target) >= 2:

                    monster.move_astar(target, entities, game_map)
                    action_cost += 1 / monster.fighter.mv_spd
                    #self.last_action += action_cost
                        
                else:
                    break

            self.last_action += action_cost

        elif self.target_seen:
            self.action_begin = False
            if not monster.x == self.target_last_seen_x and not monster.y == self.target_last_seen_y:
                monster.move_astar(target, entities, game_map)
            
        else:
            self.action_begin = False

        return combat_msg

    def choose_skill(self):
        result = []
        skill_choice = None
        if self.owner.abilities.items:
            skills = []
            attacks = []
            weights = []
            default_atk_chance = 100
            for skill in self.owner.abilities.items:
                if skill.needs_ai is True or skill.target_self is True or skill.target_other is True:
                    result.append("Skill {} not yet implemented :(".format(skill.name))
                elif skill.player_only is True:
                    continue
                elif skill.skill_type != "weapon":
                    skills.append(skill)
                    chance = skill.chance[min(self.owner.fighter.level, 2)]
                    weights.append(chance)
                    default_atk_chance -= chance

                else:
                    attacks.append(skill)

            for attack in attacks:
                skills.append(attack)
                weights.append(default_atk_chance/len(attacks))
            skill_choice = choices(skills, weights, k=1)[0]
        else:
            result.append("Monster doesn't know what to do!")
        return result, skill_choice
