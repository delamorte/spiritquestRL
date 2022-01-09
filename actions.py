from bearlibterminal import terminal as blt

from components.cursor import Cursor
from components.entity import Entity, get_neighbour_entities
from game_states import GameStates
from helpers import get_article
from ui.message_history import show_msg_history


class Actions:
    def __init__(self):
        self.owner = None

    def turn_taking_actions(self, wait=None, move=None, interact=None, pickup=None, stairs=None, examine=None):

        if wait:
            self.owner.time_counter.take_turn(1)
            # player.player.spirit_power -= 1
            self.owner.message_log.send("You wait a turn.")
            self.owner.message_log.old_stack = self.owner.message_log.stack
            self.owner.game_state = GameStates.ENEMY_TURN

        elif move:
            dx, dy = move
            destination_x = self.owner.player.x + dx
            destination_y = self.owner.player.y + dy

            # Handle player attack
            if not self.owner.levels.current_map.is_blocked(destination_x, destination_y):
                target = self.owner.levels.current_map.tiles[destination_x][destination_y].blocking_entity
                if target:
                    combat_msg = self.owner.player.fighter.attack(target, self.owner.player.player.sel_weapon)

                    self.owner.message_log.send(combat_msg)
                    # player.player.spirit_power -= 0.5
                    self.owner.time_counter.take_turn(1)
                    self.owner.render_functions.draw_stats(target)

                else:
                    if self.owner.player.fighter.mv_spd <= 0:
                        self.owner.message_log.send("You are unable to move!")
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

            self.owner.message_log.old_stack = self.owner.message_log.stack
            self.owner.message_log.stack = []

        elif interact:
            entities = get_neighbour_entities(self.owner.player, self.owner.levels.current_map.tiles)
            interact_msg = None
            for entity in entities:
                if entity.door:
                    interact_msg = entity.door.interaction(self.owner.levels.current_map)
                    self.owner.message_log.send(interact_msg)
                elif entity.item:
                    interact_msg = entity.item.interaction(self.owner.levels.current_map)
                    self.owner.message_log.send(interact_msg)
            if interact_msg:
                self.owner.time_counter.take_turn(1)
                self.owner.game_state = GameStates.ENEMY_TURN
                self.owner.fov_recompute = True

        elif pickup:
            pickup_msg = self.owner.player.inventory.add_item(self.owner.levels.current_map, self.owner.message_log)

            if pickup_msg:
                self.owner.message_log.send(pickup_msg)
                self.owner.time_counter.take_turn(1)
                self.owner.game_state = GameStates.ENEMY_TURN
                self.owner.fov_recompute = True
            else:
                self.owner.message_log.send("There is nothing here to pick up.")

        elif stairs:
            stairs_component = self.owner.levels.current_map.tiles[self.owner.player.x][self.owner.player.y].stairs
            if stairs_component:
                stairs_component.interaction(self.owner.levels, self.owner.message_log)
                self.owner.time_counter.take_turn(1)
                self.owner.render_functions.draw_messages()
                self.owner.fov_recompute = True

        elif examine:
            self.owner.game_state = GameStates.TARGETING
            cursor_component = Cursor()
            cursor = Entity(self.owner.player.x, self.owner.player.y, 4, 0xE800 + 1746, "light yellow", "cursor",
                            cursor=cursor_component, stand_on_messages=False)
            self.owner.cursor = cursor
            self.owner.levels.current_map.tiles[self.owner.cursor.x][self.owner.cursor.y].add_entity(self.owner.cursor)
            self.owner.levels.current_map.entities["cursor"] = [self.owner.cursor]
            self.owner.fov_recompute = True

    def menu_actions(self, main_menu=False, avatar_info=False, inventory=False, msg_history=False):
        if main_menu:
            self.owner.menus.main_menu.show()
            self.owner.fov_recompute = True
            return True

        if avatar_info:
            self.owner.menus.avatar_info.show()
            self.owner.fov_recompute = True
            return True

        if msg_history:
            # TODO: Refactor to use menu components
            show_msg_history(
                self.owner.message_log.history, "Message history", self.owner.ui.viewport.offset_w - 1,
                                                                   self.owner.ui.viewport.offset_h - 1)
            self.owner.ui.draw()
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
            self.owner.fov_recompute = True
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
            return True

        return False

    def targeting_actions(self, move=False, examine=False, main_menu=False):
        if move:
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

                self.owner.message_log.old_stack = self.owner.message_log.stack
                self.owner.message_log.stack = []
                if self.owner.levels.current_map.tiles[self.owner.cursor.x][self.owner.cursor.y].name is not None:
                    self.owner.message_log.stack.append(
                        self.owner.levels.current_map.tiles[self.owner.cursor.x][self.owner.cursor.y].name.capitalize())

        elif main_menu or examine:
            self.owner.game_state = GameStates.PLAYER_TURN
            self.owner.message_log.old_stack = self.owner.message_log.stack
            self.owner.message_log.stack = []
            self.owner.levels.current_map.tiles[self.owner.cursor.x][self.owner.cursor.y].remove_entity(
                self.owner.cursor)
            del self.owner.levels.current_map.entities["cursor"]
            self.owner.cursor = None
            self.owner.fov_recompute = True
            return True

        # if self.owner.player.fighter.paralyzed:
        #     self.owner.message_log.send("You are paralyzed!")
        #     self.owner.time_counter.take_turn(1)
        #     self.owner.game_state = GameStates.ENEMY_TURN

        return False

    def enemy_actions(self):
        self.owner.render_functions.draw_messages()

        for entity in self.owner.levels.current_map.entities["monsters"]:
            visible = self.owner.player.light_source.fov_map.fov[entity.y, entity.x]
            if visible:
                if entity.fighter:
                    entity.status_effects.process_effects()

                if self.owner.player.fighter.dead:
                    kill_msg = self.owner.player.kill()
                    self.owner.game_state = GameStates.PLAYER_DEAD
                    self.owner.message_log.send(kill_msg)
                    self.owner.render_functions.draw_stats()
                    self.owner.fov_recompute = True
                    break

                if entity.fighter and entity.fighter.dead:
                    level_up_msg = self.owner.player.player.handle_player_exp(entity.fighter)
                    kill_msg = entity.kill()
                    self.owner.levels.current_map.tiles[entity.x][entity.y].blocking_entity = None
                    self.owner.message_log.send(kill_msg)
                    self.owner.message_log.send("I feel my power returning!")
                    if level_up_msg:
                        self.owner.message_log.send(level_up_msg)
                    self.owner.fov_recompute = True

                elif entity.fighter and entity.fighter.paralyzed:
                    self.owner.message_log.send("The monster is paralyzed!")
                    self.owner.game_state = GameStates.PLAYER_TURN

                elif entity.ai:
                    prev_pos_x, prev_pos_y = entity.x, entity.y
                    combat_msg = entity.ai.take_turn(
                        self.owner.player, self.owner.levels.current_map, self.owner.levels.current_map.entities,
                        self.owner.time_counter)
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
                        self.owner.render_functions.draw_stats()
                    if self.owner.player.fighter.dead:
                        kill_msg = self.owner.player.kill()
                        self.owner.game_state = GameStates.PLAYER_DEAD
                        self.owner.message_log.send(kill_msg)
                        self.owner.render_functions.draw_stats()
                        break
                    # Functions on monster death
                    if entity.fighter and entity.fighter.dead:
                        level_up_msg = self.owner.player.player.handle_player_exp(entity.fighter)
                        kill_msg = entity.kill()
                        self.owner.levels.current_map.tiles[entity.x][entity.y].blocking_entity = None
                        self.owner.message_log.send(kill_msg)
                        self.owner.message_log.send("I feel my power returning!")
                        if level_up_msg:
                            self.owner.message_log.send(level_up_msg)
                        self.owner.fov_recompute = True

        if not self.owner.game_state == GameStates.PLAYER_DEAD:
            self.owner.game_state = GameStates.PLAYER_TURN
