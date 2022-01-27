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
        self.weights = {
            "heal_self": 5,
            "escape": 4,
            "ranged_attack": 2,
            "melee_attack": 4,
            "self_targeting": 1,
            "heal_buff_others": 1
        }

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

    def handle_actions(self, target, game_map, entities) -> list:
        combat_msgs = []
        while self.action_cost < self.time_to_act:

            # If player is sneaking, move randomly
            if target.player and self.cant_see_player:
                self.move_randomly(game_map)

            skill, skill_target, target_range = self.choose_skill(target, game_map)

            if skill and skill_target:
                if target.fighter.hp > 0:
                    combat_msg = self.owner.fighter.use_skill(skill_target, skill, game_map)
                    combat_msgs.extend(combat_msg)
                    self.action_cost += 1
                else:
                    break

            # If AI can't attack/use skill, try to move
            elif 1 / self.owner.fighter.mv_spd <= self.time_to_act - self.action_cost:
                self.move_action(target, entities, game_map, target_range)

            # No possible actions left, end turn
            else:
                break

        return combat_msgs

    def choose_skill(self, skill_target, game_map=None) -> tuple:
        target_range = None
        possible_skills = {
            "heal_self": [],
            "escape": [],
            "ranged_attack": [],
            "melee_attack": [],
            "self_targeting": [],
            "heal_buff_others": []
        }

        for skill in self.owner.abilities.items:

            if skill.player_only is True:
                continue

            if skill_target is not self.owner and skill.skill_type == "weapon" or skill.skill_type == "attack":
                # Check if AI has ranged attacks and that target is in range
                if skill.requires_targeting:
                    possible_skills["ranged_attack"].append(skill)
                    continue
                # Else check for melee attacks
                else:
                    possible_skills["melee_attack"].append(skill)
                    continue

            # Prevent using skills if effect already active (buffs etc)
            if skill.effect:
                for effect in skill.effect:
                    json_efx = json_data.data.status_effects[effect]
                    description = json_efx["description"]
                    if self.owner.status_effects.has_effect(description):
                        continue
                    else:
                        # Check if possible to buff self
                        if skill.target_self and not skill.name == "heal":
                            possible_skills["self_targeting"].append((skill, self.owner))

            # Check for self-healing
            if skill.name == "heal" and self.owner.fighter.hp < self.owner.fighter.max_hp:
                possible_skills["heal_self"].append((skill, self.owner))
                continue

            # Check for escape options
            if skill.name == "leap" and self.owner.fighter.hp < self.owner.fighter.max_hp:
                possible_skills["escape"].append((skill, self.owner))
                continue

            # Check if possible to buff/heal others
            if skill.target_other and self.owner.fighter.hp > ceil(0.7 * self.owner.fighter.max_hp):
                radius = skill.get_range()
                targets = game_map.get_neighbours(self.owner, radius, fighters=True,
                                                  algorithm=skill.target_area, exclude_player=True)
                if not targets:
                    continue
                if skill.name == "heal":
                    for target in targets:
                        if target.fighter.hp < target.fighter.max_hp:
                            possible_skills["heal_buff_others"].append((skill, target))
                            targets = None
                            break
                elif "boost" in skill.name:
                    for target in targets:
                        if not target.status_effects.items:
                            possible_skills["heal_buff_others"].append((skill, target))
                            targets = None
                            break
                if not targets:
                    continue

        skills = []
        weights = []

        for k, values in possible_skills.items():
            for v in values:
                skills.append(v)
                weights.append(self.weights[k])

        # If no possible actions
        if not skills:
            skill_choice = None
        else:
            skill_choice = choices(skills, weights, k=1)[0]

        # If skill == buff/heal other == (skill, target)
        if isinstance(skill_choice, tuple):
            x, y = skill_choice[0], skill_choice[1]
            skill_choice, skill_target = x, y

        if skill_choice.target_area == "melee" and self.owner.distance_to(skill_target) > 1:
            # Set skill choice to None, will try to move closer to target
            skill_choice = None

        elif skill_choice.requires_targeting and skill_target is not self.owner:
            target_range = self.owner.distance_to(skill_target)
            if target_range > skill_choice.get_range():
                skill_choice = None

        return skill_choice, skill_target, target_range

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

    def move_action(self, target, entities, game_map, target_range):
        self.follow_player(target, entities, game_map)
