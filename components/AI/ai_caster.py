from math import ceil
from random import choices, randint, choice

from components.AI.ai_basic import AIBasic
from components.animation import Animation
from data import json_data
from ui.message import Message


class AICaster(AIBasic):
    def __init__(self, ally=False):
        super().__init__(ally=ally)

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

    def choose_skill(self, game_map=None, skill_target=None):
        skill_choice = None
        if self.owner.abilities.items:
            skills = []
            attacks = []
            weights = []
            default_atk_chance = 1.0
            for skill in self.owner.abilities.items:
                skip = False
                if skill.player_only is True:
                    continue
                elif skill.skill_type != "weapon":
                    chance = skill.chance[skill.rank]

                    # Prevent using skills if effect already active (buffs etc)
                    if skill.effect:
                        for effect in skill.effect:
                            json_efx = json_data.data.status_effects[effect]
                            description = json_efx["description"]
                            if skill_target.status_effects.has_effect(description):
                                skip = True
                    if skip and not skill.target_other:
                        continue
                    if skill.name == "heal":
                        if self.owner.fighter.hp < self.owner.fighter.max_hp:
                            chance += 0.2

                    if skill.name == "leap" and self.owner.fighter.hp < self.owner.fighter.max_hp:
                        chance += 0.2

                    # Buff/heal others
                    if skill.target_other and self.owner.fighter.hp > ceil(0.7 * self.owner.fighter.max_hp):
                        radius = skill.get_range()
                        targets = game_map.get_neighbours(self.owner, radius, fighters=True,
                                                          algorithm=skill.target_area, exclude_player=True)
                        if not targets:
                            continue
                        if skill.name == "heal":
                            for target in targets:
                                if target.fighter.hp < target.fighter.max_hp:
                                    skill_target = target
                                    break
                        elif "boost" in skill.name:
                            for target in targets:
                                if not target.stauts_effects.items:
                                    skill_target = target
                                    break
                        if skill_target is None:
                            continue

                    skills.append(skill)
                    weights.append(chance)
                    default_atk_chance -= chance

                else:
                    attacks.append(skill)

            if attacks:
                for attack in attacks:
                    skills.append(attack)
                    weights.append(default_atk_chance/len(attacks))

            if skills:
                skill_choice = choices(skills, weights, k=1)[0]
                if not skill_choice.target_other:
                    skill_target = None

        return skill_choice, skill_target
