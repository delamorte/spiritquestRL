from math import ceil
from random import choices, randint, choice
from components.animation import Animation
from data import json_data
from ui.message import Message


class AIBasic:
    def __init__(self, ally=False):
        self.owner = None
        self.action_cost = 0
        self.time_to_act = 0
        self.action_begin = False
        self.last_action = 0
        self.target_seen = False
        self.ally = ally
        self.target_last_seen_x = 0
        self.target_last_seen_y = 0
        self.wait_first_turn = False
        self.cant_see_player = False
        self.path = None
        self.can_heal = None
        self.can_leap = None
        if ally:
            self.wait_first_turn = True

    def take_turn(self, target, game_map, entities, time):
        if self.wait_first_turn:
            self.wait_first_turn = False
            return None
        if not self.action_begin:
            self.last_action = time.get_last_turn()
        self.time_to_act = time.get_turn() - self.last_action
        self.action_cost = 0
        combat_msgs = []

        if target.player and not target.status_effects.has_effect("sneaking"):
            self.cant_see_player = False

        # If ally, follow player or chance to move randomly if already next to player
        if self.ally and target.player:
            self.follow_player(target, entities, game_map)

        elif game_map.visible[target.x, target.y]:

            self.target_seen = True
            if self.path and (target.x != self.target_last_seen_x or target.y != self.target_last_seen_y):
                self.path = None
            self.target_last_seen_x = target.x
            self.target_last_seen_y = target.y
            self.action_begin = True

            combat_msgs.extend(self.handle_actions(target, game_map, entities))

            self.last_action += self.action_cost

        self.owner.remark(sneak=self.cant_see_player)
        return combat_msgs

    def choose_skill(self, game_map=None, skill_target=None):
        skill_choice = None
        if self.owner.abilities.items:
            skills = []
            attacks = []
            weights = []
            default_atk_chance = 1.0
            for skill in self.owner.abilities.items:
                if skill.player_only is True:
                    continue
                elif skill.skill_type != "weapon":
                    skills.append(skill)
                    chance = skill.chance[skill.rank]
                    weights.append(chance)
                    default_atk_chance -= chance

                else:
                    attacks.append(skill)

            for attack in attacks:
                skills.append(attack)
                weights.append(default_atk_chance / len(attacks))
            skill_choice = choices(skills, weights, k=1)[0]

        return skill_choice, skill_target

    def follow_player(self, target, entities, game_map):
        if self.owner.distance_to(target) > 1:
            if self.path:
                self.owner.x, self.owner.y = self.path.pop(0)
            else:
                self.path = self.owner.get_path_to(target, entities, game_map)
                if self.path:
                    self.owner.x, self.owner.y = self.path.pop(0)

            self.action_cost += 1 / self.owner.fighter.mv_spd
        elif randint(0, 4) == 0:
            self.move_randomly(game_map)

    def handle_actions(self, target, game_map, entities) -> list:
        combat_msgs = []
        while self.action_cost < self.time_to_act:

            # If player is sneaking, move randomly
            if target.player and self.cant_see_player:
                self.move_randomly(game_map)

            skill, skill_target = self.choose_skill(game_map, target)

            if skill:
                if skill_target:
                    target = skill_target
                radius = skill.get_range()

                # Use self targeting skills
                if target == self.owner:
                    if target.fighter.hp > 0:
                        combat_msg = self.owner.fighter.use_skill(self.owner, skill, game_map)
                        combat_msgs.extend(combat_msg)
                        self.action_cost += 1
                    else:
                        break

                # Use ranged skill
                elif skill.requires_targeting and self.owner.distance_to(target) <= radius:
                    if target.fighter.hp > 0:
                        combat_msg = self.owner.fighter.use_skill(target, skill)
                        combat_msgs.extend(combat_msg)
                        self.action_cost += 1
                    else:
                        break

                # If enough 'action points' and in melee range, attack
                elif self.owner.distance_to(target) == 1 and\
                        (self.owner.fighter.atk_spd <= self.time_to_act - self.action_cost):
                    if target.fighter.hp > 0:

                        combat_msg = self.owner.fighter.use_skill(target, skill)
                        combat_msgs.extend(combat_msg)
                        self.action_cost += 1

                    else:
                        break

            # Move closer to player
            elif 1 / self.owner.fighter.mv_spd <= self.time_to_act - self.action_cost:
                self.follow_player(target, entities, game_map)

            else:
                # No possible actions
                combat_msgs.append(Message("{0} doesn't know what to do!".format(self.owner.name)))
                break

        return combat_msgs

    def prepare_skills(self):
        for skill in self.owner.abilities.items:
            if skill.name == "heal":
                self.can_heal = True
            if skill.name == "leap":
                self.can_leap = True

    def move_randomly(self, game_map):
        tiles = game_map.get_neighbours(self.owner, algorithm="square", empty_tiles=True)
        target_tile = choice(tiles)
        self.owner.move_to_tile(target_tile.x, target_tile.y)
        self.action_cost += 1 / self.owner.fighter.mv_spd

    def move_to_last_known_location(self, target, game_map, entities):
        # Try to move to last known target location
        self.action_cost = 0
        self.action_begin = False
        if not self.owner.x == self.target_last_seen_x and not self.owner.y == self.target_last_seen_y:
            if target.x == self.target_last_seen_x and target.y == self.target_last_seen_y and self.path:
                self.owner.x, self.owner.y = self.path.pop(0)
            else:
                self.path = self.owner.get_path_to(target, entities, game_map)
                if self.path:
                    self.owner.x, self.owner.y = self.path.pop(0)
            self.action_cost += 1 / self.owner.fighter.mv_spd
            self.last_action += self.action_cost
        else:
            self.target_seen = False
            self.last_action = 0


