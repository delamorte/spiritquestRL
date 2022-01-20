from random import choices, randint, choice
from ui.message import Message


class BasicMonster:
    def __init__(self, ally=False):
        self.owner = None
        self.action_begin = False
        self.last_action = 0
        self.target_seen = False
        self.ally = ally
        self.target_last_seen_x = 0
        self.target_last_seen_y = 0
        self.wait_first_turn = False
        self.cant_see_player = False
        self.path = None
        if ally:
            self.wait_first_turn = True

    def take_turn(self, target, game_map, entities, time):
        if self.wait_first_turn:
            self.wait_first_turn = False
            return None
        if not self.action_begin:
            self.last_action = time.get_last_turn()
        time_to_act = time.get_turn() - self.last_action
        action_cost = 0
        combat_msgs = []

        if target.player and not target.fighter.sneaking:
            self.cant_see_player = False

        if self.ally and target.player:
            if self.owner.distance_to(target) > 1:
                if target.x == self.target_last_seen_x and target.y == self.target_last_seen_y and self.path:
                    self.owner.x, self.owner.y = self.path.pop(0)
                else:
                    self.path = self.owner.get_path_to(target, entities, game_map)
                    if self.path:
                        self.owner.x, self.owner.y = self.path.pop(0)
            elif randint(0, 4) == 0:
                tiles = game_map.get_neighbours(self.owner, algorithm="square", empty_tiles=True)
                target_tile = choice(tiles)
                self.owner.move_to_tile(target_tile.x, target_tile.y)
                if self.owner.remarks:
                    remark = choice(self.owner.remarks)
                    combat_msgs.append(Message("{0}: {1}".format(self.owner.colored_name, remark),
                                               style="dialog"))

        elif game_map.visible[target.x, target.y]:

            self.target_seen = True
            if self.path and (target.x != self.target_last_seen_x or target.y != self.target_last_seen_y):
                self.path = None
            self.target_last_seen_x = target.x
            self.target_last_seen_y = target.y
            self.action_begin = True

            while action_cost < time_to_act:

                if self.owner.distance_to(target) == 1 and self.owner.fighter.atk_spd <= time_to_act - action_cost:
                    if target.fighter.hp > 0:
                        combat_msg, skill = self.choose_skill()
                        if skill is None:
                            combat_msgs.extend(combat_msg)
                            return combat_msgs
                        combat_msg = self.owner.fighter.attack(target, skill)
                        combat_msgs.extend(combat_msg)
                        action_cost += 1
                        # self.last_action += action_cost

                    else:
                        break

                elif target.player and self.cant_see_player:
                    tiles = game_map.get_neighbours(self.owner, algorithm="square", empty_tiles=True)
                    target_tile = choice(tiles)
                    self.owner.move_to_tile(target_tile.x, target_tile.y)
                    combat_msgs.append(Message("{0}: Come out, wherever you are.".format(self.owner.colored_name),
                                               style="dialog"))
                    action_cost += 1 / self.owner.fighter.mv_spd

                elif 1 / self.owner.fighter.mv_spd <= time_to_act - action_cost and self.owner.distance_to(target) >= 2:
                    if randint(0, 4) == 0:
                        if self.owner.remarks:
                            remark = choice(self.owner.remarks)
                            combat_msgs.append(
                                Message(msg="{0}: {1}".format(self.owner.colored_name, remark),
                                        style="dialog"))
                    if self.path:
                        self.owner.x, self.owner.y = self.path.pop(0)
                    else:
                        self.path = self.owner.get_path_to(target, entities, game_map)
                        if self.path:
                            self.owner.x, self.owner.y = self.path.pop(0)

                    action_cost += 1 / self.owner.fighter.mv_spd
                    # self.last_action += action_cost

                else:
                    break

            self.last_action += action_cost

        return combat_msgs

    def choose_skill(self):
        result = []
        skill_choice = None
        if self.owner.abilities.items:
            skills = []
            attacks = []
            weights = []
            default_atk_chance = 1.0
            for skill in self.owner.abilities.items:
                if skill.needs_ai is True or skill.target_self is True or skill.target_other is True:
                    result.append("Skill {0} not yet implemented :(".format(skill.name))
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
            result.append("{0} doesn't know what to do!".format(self.owner.name))
        return result, skill_choice

    def move_to_last_known_location(self, target, game_map, entities):
        # Try to move to last known target location
        action_cost = 0
        self.action_begin = False
        if not self.owner.x == self.target_last_seen_x and not self.owner.y == self.target_last_seen_y:
            if target.x == self.target_last_seen_x and target.y == self.target_last_seen_y and self.path:
                self.owner.x, self.owner.y = self.path.pop(0)
            else:
                self.path = self.owner.get_path_to(target, entities, game_map)
                if self.path:
                    self.owner.x, self.owner.y = self.path.pop(0)
            action_cost += 1 / self.owner.fighter.mv_spd
            self.last_action += action_cost
        else:
            self.target_seen = False
            self.last_action = 0
