from bearlibterminal import terminal as blt

from components.cursor import Cursor
from components.entity import Entity
from game_states import GameStates
from helpers import get_article
from ui.message import Message
from ui.message_history import show_msg_history


class Actions:
    def __init__(self):
        self.owner = None

    def turn_taking_actions(self, wait=None, move=None, interact=None, pickup=None, stairs=None, examine=None,
                            use_ability=None, key=None):

        msg = self.owner.player.summoner.process(game_map=self.owner.levels.current_map)
        if msg:
            self.owner.message_log.send(msg)
        self.owner.fov_recompute = True

        if wait or move or interact or pickup or stairs or use_ability and not self.owner.player.dead:
            self.owner.player.status_effects.process_effects(game_map=self.owner.levels.current_map)
            if self.owner.player.status_effects.has_effect("paralyzed"):
                msg = Message("You are paralyzed!")
                self.owner.message_log.send(msg)
                self.owner.time_counter.take_turn(1)
                self.owner.fov_recompute = True
                return

        if wait:
            self.owner.time_counter.take_turn(1)
            # player.player.spirit_power -= 1
            msg = Message("You wait a turn.")
            self.owner.message_log.send(msg)
            self.owner.game_state = GameStates.ENEMY_TURN
            self.owner.fov_recompute = True

        elif move:
            dx, dy = move
            destination_x = self.owner.player.x + dx
            destination_y = self.owner.player.y + dy

            # Handle player attack
            if not self.owner.levels.current_map.is_blocked(destination_x, destination_y):
                target = self.owner.levels.current_map.tiles[destination_x][destination_y].blocking_entity
                if target:
                    if self.owner.player.status_effects.has_effect("stunned"):
                        msg = Message("You are stunned and unable to act!")
                        self.owner.message_log.send(msg)
                        return
                    else:
                        results = self.owner.player.fighter.use_skill(target, self.owner.player.player.sel_weapon)
                        self.owner.message_log.send(results)
                        # player.player.spirit_power -= 0.5
                        self.owner.time_counter.take_turn(1)
                        self.owner.render_functions.draw_stats(target)

                else:
                    if self.owner.player.fighter.mv_spd <= 0:
                        msg = Message("You are unable to move!")
                        self.owner.message_log.send(msg)
                        self.owner.time_counter.take_turn(1)
                    else:
                        prev_pos_x, prev_pos_y = self.owner.player.x, self.owner.player.y
                        self.owner.player.move(dx, dy)
                        self.owner.time_counter.take_turn(1 / self.owner.player.fighter.mv_spd)
                        self.owner.fov_recompute = True
                        self.owner.levels.current_map.tiles[prev_pos_x][prev_pos_y].remove_entity(self.owner.player)
                        self.owner.levels.current_map.tiles[self.owner.player.x][self.owner.player.y].add_entity(
                            self.owner.player)

                self.owner.game_state = GameStates.ENEMY_TURN

            elif self.owner.levels.current_map.tiles[destination_x][destination_y].is_door:
                door = self.owner.levels.current_map.tiles[destination_x][destination_y].door
                interact_msg = door.interaction(self.owner.levels.current_map)
                self.owner.message_log.send(interact_msg)
                self.owner.time_counter.take_turn(1)
                self.owner.game_state = GameStates.ENEMY_TURN
                self.owner.fov_recompute = True

        elif interact:
            entities = self.owner.levels.current_map.get_neighbours(self.owner.player)
            interact_msg = None
            for entity in entities:
                if entity.door:
                    interact_msg = entity.door.interaction(self.owner.levels.current_map)
                    if interact_msg:
                        self.owner.message_log.send(interact_msg)
                elif entity.item:
                    interact_msg = entity.item.interaction(self.owner.levels.current_map)
                    if interact_msg:
                        self.owner.message_log.send(interact_msg)
            if interact_msg:
                self.owner.time_counter.take_turn(1)
                self.owner.game_state = GameStates.ENEMY_TURN
                self.owner.fov_recompute = True

        elif pickup:
            pickup_msg = self.owner.player.inventory.add_item(self.owner.levels.current_map)

            if pickup_msg:
                self.owner.message_log.send(pickup_msg)
                self.owner.time_counter.take_turn(1)
                self.owner.game_state = GameStates.ENEMY_TURN
                self.owner.fov_recompute = True
            else:
                msg = Message("There is nothing here to pick up.")
                self.owner.message_log.send(msg)

        elif stairs:
            stairs_component = self.owner.levels.current_map.tiles[self.owner.player.x][self.owner.player.y].stairs
            if stairs_component:
                results = stairs_component.interaction(self.owner.levels)
                self.owner.message_log.send(results)
                self.owner.time_counter.take_turn(1)
                self.owner.render_functions.draw_messages()
                self.owner.fov_recompute = True

        elif examine:
            self.owner.game_state = GameStates.TARGETING
            cursor_component = Cursor()
            cursor = Entity(self.owner.player.x, self.owner.player.y, 5, 0xF000 + 9, "light yellow", "cursor",
                            cursor=cursor_component, stand_on_messages=False)
            self.owner.cursor = cursor
            self.owner.levels.current_map.tiles[self.owner.cursor.x][self.owner.cursor.y].add_entity(self.owner.cursor)
            self.owner.levels.current_map.entities["cursor"] = [self.owner.cursor]
            self.owner.fov_recompute = True

        elif use_ability:
            if key == blt.TK_Z:
                ability = self.owner.player.player.sel_utility
            else:
                ability = self.owner.player.player.sel_attack
            result, target, targeting = self.owner.player.player.use_ability(self.owner.levels.current_map, ability)
            if target:
                self.owner.render_functions.draw_stats(target)
            if targeting:
                self.owner.game_state = GameStates.TARGETING

                cursor_component = Cursor(targeting_ability=ability)
                cursor = Entity(target.x, target.y, 5, 0xF000 + 9, "light yellow", "cursor",
                                cursor=cursor_component, stand_on_messages=False)
                self.owner.cursor = cursor
                self.owner.levels.current_map.tiles[self.owner.cursor.x][self.owner.cursor.y].add_entity(
                    self.owner.cursor)
                self.owner.levels.current_map.entities["cursor"] = [self.owner.cursor]

            self.owner.message_log.send(result)
            self.owner.fov_recompute = True

        if self.owner.player.status_effects.has_effect("summoning"):
            msg = self.owner.player.summoner.process(game_map=self.owner.levels.current_map)
            if msg:
                self.owner.message_log.send(msg)
            self.owner.fov_recompute = True

        if not self.owner.cursor:
            self.owner.animations_buffer.extend(self.owner.player.animations.buffer)
            self.owner.player.animations.buffer = []

        return False

    def menu_actions(self, main_menu=False, avatar_info=False, inventory=False, msg_history=False,
                     level_up=False):
        if main_menu:
            self.owner.menus.main_menu.show()
            self.owner.fov_recompute = True
            return True

        if avatar_info:
            self.owner.menus.avatar_info.show()
            self.owner.fov_recompute = True
            return True

        if level_up:
            results = self.owner.menus.level_up.show()
            if results:
                self.owner.message_log.send(results)
            self.owner.fov_recompute = True
            return True

        if msg_history:
            # TODO: Refactor to use menu components
            show_msg_history(
                self.owner.message_log.history, "Message history", self.owner.ui.viewport.offset_w - 1,
                                                                   self.owner.ui.viewport.offset_h - 1)
            self.owner.ui.draw()
            self.owner.ui.side_panel.draw_content()
            self.owner.fov_recompute = True
            return True

        if inventory:
            # TODO: Refactor to use menu components
            show_items = []
            for item in self.owner.player.inventory.items:
                show_items.append(get_article(item.name) + " " + item.name)
            show_msg_history(
                show_items, "Inventory", self.owner.ui.viewport.offset_w - 1, self.owner.ui.viewport.offset_h - 1)
            self.owner.ui.draw()
            self.owner.ui.side_panel.draw_content()
            self.owner.fov_recompute = True
            return True

        return False

    def ability_actions(self, switch=None, key=None):
        if switch and key:
            if key == blt.TK_W:
                self.owner.player.player.switch_weapon()
            elif key == blt.TK_A:
                self.owner.player.player.switch_attack()
            else:
                for ability in self.owner.player.abilities.utility_skills:
                    if key == ability.blt_input:
                        self.owner.player.player.sel_utility = ability
                        self.owner.player.player.sel_utility_idx = ability.blt_input - 30  # get list index, 30 == blt.TK_1
                        break
            self.owner.ui.side_panel.draw_content()
            return True
        return False

    def window_actions(self, fullscreen=False, close=False):
        if fullscreen:
            blt.set("window.fullscreen=true")
            self.owner.fov_recompute = True
            return True

        if close:
            blt.close()

        return False

    def dead_actions(self, key):
        if key == blt.TK_CLOSE:
            blt.close()

        if key == blt.TK_ESCAPE:
            self.owner.menus.main_menu.show()
            self.owner.fov_recompute = True
            #self.owner.game_state = GameStates.PLAYER_DEAD
            return True

        return False

    def targeting_actions(self, move=False, examine=False, main_menu=False, use_ability=False,
                          interact=False):

        if move:
            if self.owner.cursor.cursor.targeting_ability:
                include_self = self.owner.cursor.cursor.targeting_ability.target_self
                radius = self.owner.cursor.cursor.targeting_ability.get_range()
                area = self.owner.cursor.cursor.targeting_ability.target_area
                entities = self.owner.levels.current_map.get_neighbours(self.owner.player, radius,
                                          include_self=include_self, fighters=True, mark_area=True, algorithm=area)
                msg = self.owner.cursor.cursor.select_next(entities, self.owner.levels.current_map.tiles)
                if msg:
                    self.owner.message_log.send(msg)
                self.owner.fov_recompute = True

            else:
                dx, dy = move
                destination_x = self.owner.cursor.x + dx
                destination_y = self.owner.cursor.y + dy
                x, y = self.owner.game_camera.get_coordinates(destination_x, destination_y)

                if 0 < x < self.owner.game_camera.width - 1 and 0 < y < self.owner.game_camera.height - 1:
                    prev_pos_x, prev_pos_y = self.owner.cursor.x, self.owner.cursor.y
                    self.owner.cursor.move(dx, dy)
                    self.owner.levels.current_map.tiles[prev_pos_x][prev_pos_y].remove_entity(self.owner.cursor)
                    self.owner.levels.current_map.tiles[self.owner.cursor.x][self.owner.cursor.y].add_entity(
                        self.owner.cursor)
                    self.owner.fov_recompute = True

        elif main_menu or examine:
            self.owner.game_state = GameStates.PLAYER_TURN
            self.owner.levels.current_map.tiles[self.owner.cursor.x][self.owner.cursor.y].remove_entity(
                self.owner.cursor)
            del self.owner.levels.current_map.entities["cursor"]
            self.owner.cursor = None
            self.owner.fov_recompute = True
            return True

        elif (use_ability or interact) and self.owner.cursor.cursor.targeting_ability:
            target = self.owner.levels.current_map.tiles[self.owner.cursor.x][self.owner.cursor.y].blocking_entity

            result, target, targeting = self.owner.player.player.use_ability(self.owner.levels.current_map,
                                                             self.owner.cursor.cursor.targeting_ability, target)
            if target:
                self.owner.render_functions.draw_stats(target)
            self.owner.time_counter.take_turn(1)
            self.owner.game_state = GameStates.ENEMY_TURN
            self.owner.message_log.send(result)
            self.owner.levels.current_map.tiles[self.owner.cursor.x][self.owner.cursor.y].remove_entity(
                self.owner.cursor)
            del self.owner.levels.current_map.entities["cursor"]
            self.owner.cursor = None
            self.owner.fov_recompute = True
            self.owner.animations_buffer.extend(self.owner.player.animations.buffer)
            self.owner.player.animations.buffer = []

        return False

    def enemy_actions(self):
        self.owner.render_functions.draw_messages()

        for entity in self.owner.levels.current_map.entities["monsters"]:
            entity.visible = False
            visible = self.owner.levels.current_map.visible[entity.x, entity.y]
            if visible:
                entity.visible = True
                if entity.fighter:
                    entity.status_effects.process_effects()
                    self.owner.render_functions.draw_stats(entity)

                if self.owner.player.dead:
                    kill_msg = self.owner.player.kill()
                    self.owner.game_state = GameStates.PLAYER_DEAD
                    self.owner.message_log.send(kill_msg)
                    self.owner.render_functions.draw_stats()
                    self.owner.fov_recompute = True
                    break

                if entity.fighter and entity.dead:
                    level_up_msg = self.owner.player.player.handle_player_exp(entity.fighter)
                    kill_msg = entity.kill()
                    self.owner.levels.current_map.tiles[entity.x][entity.y].blocking_entity = None
                    self.owner.message_log.send(kill_msg)
                    self.owner.message_log.send(Message("I feel my power returning!"))
                    if level_up_msg:
                        self.owner.message_log.send(level_up_msg)
                    self.owner.fov_recompute = True

                elif entity.fighter and entity.status_effects.has_effect("paralyzed"):
                    self.owner.message_log.send(Message("The monster is paralyzed!"))
                    self.owner.game_state = GameStates.PLAYER_TURN

                elif entity.ai:
                    prev_pos_x, prev_pos_y = entity.x, entity.y
                    combat_msg = entity.ai.take_turn(
                        self.owner.player, self.owner.levels.current_map, self.owner.levels.current_map.entities,
                        self.owner.time_counter)
                    self.owner.animations_buffer.extend(entity.animations.buffer)
                    entity.animations.buffer = []
                    self.owner.levels.current_map.tiles[prev_pos_x][prev_pos_y].remove_entity(entity)
                    self.owner.levels.current_map.tiles[entity.x][entity.y].add_entity(entity)
                    if entity.occupied_tiles is not None:
                        self.owner.levels.current_map.tiles[prev_pos_x][prev_pos_y + 1].remove_entity(entity)
                        self.owner.levels.current_map.tiles[prev_pos_x + 1][prev_pos_y + 1].remove_entity(entity)
                        self.owner.levels.current_map.tiles[prev_pos_x + 1][prev_pos_y].remove_entity(entity)

                        self.owner.levels.current_map.tiles[entity.x][entity.y + 1].add_entity(entity)
                        self.owner.levels.current_map.tiles[entity.x + 1][entity.y + 1].add_entity(entity)
                        self.owner.levels.current_map.tiles[entity.x + 1][entity.y].add_entity(entity)

                    self.owner.fov_recompute = True
                    if combat_msg:
                        self.owner.message_log.send(combat_msg)
                        self.owner.render_functions.draw_stats(entity)
                    if self.owner.player.dead:
                        kill_msg = self.owner.player.kill()
                        self.owner.game_state = GameStates.PLAYER_DEAD
                        self.owner.message_log.send(kill_msg)
                        self.owner.render_functions.draw_stats()
                        break
                    # Functions on monster death
                    if entity.fighter and entity.dead:
                        level_up_msg = self.owner.player.player.handle_player_exp(entity.fighter)
                        kill_msg = entity.kill()
                        self.owner.levels.current_map.tiles[entity.x][entity.y].blocking_entity = None
                        self.owner.message_log.send(kill_msg)
                        self.owner.message_log.send(Message("I feel my power returning!"))
                        if level_up_msg:
                            self.owner.message_log.send(level_up_msg)
                        self.owner.fov_recompute = True
            elif entity.ai and entity.ai.target_seen:
                entity.ai.move_to_last_known_location(self.owner.player,
                                                      self.owner.levels.current_map,
                                                      self.owner.levels.current_map.entities)

        if not self.owner.game_state == GameStates.PLAYER_DEAD:
            self.owner.game_state = GameStates.PLAYER_TURN

    def ally_actions(self):

        for entity in self.owner.levels.current_map.entities["allies"]:
            entity.visible = False
            visible = self.owner.levels.current_map.visible[entity.x, entity.y]
            if visible:
                entity.visible = True
                if entity.fighter:
                    entity.status_effects.process_effects()
                    self.owner.render_functions.draw_stats(entity)

                if self.owner.player.dead:
                    kill_msg = self.owner.player.kill()
                    self.owner.game_state = GameStates.PLAYER_DEAD
                    self.owner.message_log.send(kill_msg)
                    self.owner.render_functions.draw_stats()
                    self.owner.fov_recompute = True
                    break

                if entity.fighter and entity.dead:
                    entity.kill()
                    self.owner.player.summoner.end_summoning(game_map=self.owner.levels.current_map)
                    self.owner.levels.current_map.tiles[entity.x][entity.y].blocking_entity = None
                    self.owner.fov_recompute = True
                    del entity
                    return

                elif entity.fighter and entity.status_effects.has_effect("paralyzed"):
                    self.owner.message_log.send(Message("Your {0} friend is paralyzed!".format(entity.name)))
                    self.owner.game_state = GameStates.PLAYER_TURN

                elif entity.ai:
                    target = self.owner.player
                    prev_pos_x, prev_pos_y = entity.x, entity.y
                    # TODO: Implement ally AI component
                    targets = self.owner.levels.current_map.get_neighbours(entity, radius=3, fighters=True,
                                                                           exclude_player=True)
                    if targets:
                        target = targets[0]

                    combat_msg = entity.ai.take_turn(
                        target, self.owner.levels.current_map, self.owner.levels.current_map.entities,
                        self.owner.time_counter)
                    self.owner.animations_buffer.extend(entity.animations.buffer)
                    entity.animations.buffer = []
                    self.owner.levels.current_map.tiles[prev_pos_x][prev_pos_y].remove_entity(entity)
                    self.owner.levels.current_map.tiles[entity.x][entity.y].add_entity(entity)
                    if entity.occupied_tiles is not None:
                        self.owner.levels.current_map.tiles[prev_pos_x][prev_pos_y + 1].remove_entity(entity)
                        self.owner.levels.current_map.tiles[prev_pos_x + 1][prev_pos_y + 1].remove_entity(entity)
                        self.owner.levels.current_map.tiles[prev_pos_x + 1][prev_pos_y].remove_entity(entity)

                        self.owner.levels.current_map.tiles[entity.x][entity.y + 1].add_entity(entity)
                        self.owner.levels.current_map.tiles[entity.x + 1][entity.y + 1].add_entity(entity)
                        self.owner.levels.current_map.tiles[entity.x + 1][entity.y].add_entity(entity)

                    self.owner.fov_recompute = True
                    if combat_msg:
                        self.owner.message_log.send(combat_msg)
                        self.owner.render_functions.draw_stats(entity)
                    if self.owner.player.dead:
                        kill_msg = self.owner.player.kill()
                        self.owner.game_state = GameStates.PLAYER_DEAD
                        self.owner.message_log.send(kill_msg)
                        self.owner.render_functions.draw_stats()
                        break
                    # Functions on monster death
                    if entity.fighter and entity.dead:
                        level_up_msg = self.owner.player.player.handle_player_exp(entity.fighter)
                        kill_msg = entity.kill()
                        self.owner.levels.current_map.tiles[entity.x][entity.y].blocking_entity = None
                        self.owner.message_log.send(kill_msg)
                        self.owner.message_log.send(Message("I feel my power returning!"))
                        if level_up_msg:
                            self.owner.message_log.send(level_up_msg)
                        self.owner.fov_recompute = True
