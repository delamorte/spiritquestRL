from bearlibterminal import terminal as blt

from components.cursor import Cursor
from components.entity import blocking_entity, Entity
from death_functions import kill_player, kill_monster
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
                target = blocking_entity(
                    self.owner.levels.current_map.entities, destination_x, destination_y)
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
                        if self.owner.player in self.owner.levels.current_map.tiles[prev_pos_x][prev_pos_y].entities_on_tile:
                            self.owner.levels.current_map.tiles[prev_pos_x][prev_pos_y].entities_on_tile.remove(self.owner.player)
                        self.owner.levels.current_map.tiles[self.owner.player.x][self.owner.player.y].entities_on_tile.append(self.owner.player)

                self.owner.game_state = GameStates.ENEMY_TURN

            elif self.owner.levels.current_map.tiles[destination_x][destination_y].is_door:
                door = self.owner.levels.current_map.tiles[destination_x][destination_y].door
                if door.status == "locked":
                    self.owner.message_log.send("The door is locked...")
                    self.owner.time_counter.take_turn(1)
                    self.owner.game_state = GameStates.ENEMY_TURN
                elif door.status == "closed":
                    door.set_status("open", self.owner.levels.current_map)
                    self.owner.message_log.send("You open the door.")
                    self.owner.time_counter.take_turn(1)
                    self.owner.game_state = GameStates.ENEMY_TURN
                    self.owner.fov_recompute = True

            self.owner.message_log.old_stack = self.owner.message_log.stack
            self.owner.message_log.stack = []

        elif interact:
            if "doors" in self.owner.levels.current_map.entities:
                # TODO: make better function to check neighboring tiles
                for entity in self.owner.levels.current_map.entities["doors"]:
                    if ((entity.x, entity.y) == (self.owner.player.x - 1, self.owner.player.y) or
                            (entity.x, entity.y) == (self.owner.player.x - 1, self.owner.player.y - 1) or
                            (entity.x, entity.y) == (self.owner.player.x, self.owner.player.y - 1) or
                            (entity.x, entity.y) == (self.owner.player.x + 1, self.owner.player.y - 1) or
                            (entity.x, entity.y) == (self.owner.player.x + 1, self.owner.player.y) or
                            (entity.x, entity.y) == (self.owner.player.x + 1, self.owner.player.y + 1) or
                            (entity.x, entity.y) == (self.owner.player.x, self.owner.player.y + 1) or
                            (entity.x, entity.y) == (self.owner.player.x - 1, self.owner.player.y + 1)):
                        if entity.door.status == "closed":
                            entity.door.set_status("open", self.owner.levels.current_map)
                            self.owner.message_log.send("You open the door.")
                            self.owner.time_counter.take_turn(1)
                            self.owner.game_state = GameStates.ENEMY_TURN
                        elif entity.door.status == "open":
                            entity.door.set_status("closed", self.owner.levels.current_map)
                            self.owner.message_log.send("You close the door.")
                            self.owner.time_counter.take_turn(1)
                            self.owner.game_state = GameStates.ENEMY_TURN
                        else:
                            self.owner.message_log.send("The door is locked.")
                            self.owner.time_counter.take_turn(1)
                            self.owner.game_state = GameStates.ENEMY_TURN
            if "items" in self.owner.levels.current_map.entities:
                for entity in self.owner.levels.current_map.entities["items"]:
                    if ((entity.x, entity.y) == (self.owner.player.x - 1, self.owner.player.y) or
                            (entity.x, entity.y) == (self.owner.player.x - 1, self.owner.player.y - 1) or
                            (entity.x, entity.y) == (self.owner.player.x, self.owner.player.y - 1) or
                            (entity.x, entity.y) == (self.owner.player.x + 1, self.owner.player.y - 1) or
                            (entity.x, entity.y) == (self.owner.player.x + 1, self.owner.player.y) or
                            (entity.x, entity.y) == (self.owner.player.x + 1, self.owner.player.y + 1) or
                            (entity.x, entity.y) == (self.owner.player.x, self.owner.player.y + 1) or
                            (entity.x, entity.y) == (self.owner.player.x, self.owner.player.y) or
                            (entity.x, entity.y) == (self.owner.player.x - 1, self.owner.player.y + 1)):

                        interact_msg = entity.item.interaction(self.owner.levels.current_map)
                        if interact_msg:
                            self.owner.message_log.send(interact_msg)
                            self.owner.fov_recompute = True

        elif pickup:
            if "items" in self.owner.levels.current_map.entities:
                for entity in self.owner.levels.current_map.entities["items"]:
                    if entity.x == self.owner.player.x and entity.y == self.owner.player.y and entity.item.pickable:
                        pickup_msg = self.owner.player.inventory.add_item(entity)
                        self.owner.message_log.send(pickup_msg)
                        for item in self.owner.message_log.stack:
                            if entity.name == item.split(" ", 1)[1]:
                                self.owner.message_log.stack.remove(item)
                        self.owner.levels.current_map.tiles[entity.x][entity.y].entities_on_tile.remove(entity)
                        self.owner.levels.current_map.entities["items"].remove(entity)
                        self.owner.time_counter.take_turn(1)
                        self.owner.game_state = GameStates.ENEMY_TURN
                        self.owner.fov_recompute = True
                        break
                    # else:
                    #     message_log.send("There is nothing here to pick up.")
            else:
                self.owner.message_log.send("There is nothing here to pick up.")

        elif stairs:
            if "stairs" in self.owner.levels.current_map.entities:
                for entity in self.owner.levels.current_map.entities["stairs"]:
                    if self.owner.player.x == entity.x and self.owner.player.y == entity.y:
                        self.owner.levels.change(entity.stairs.destination[0])

                self.owner.message_log.old_stack = self.owner.message_log.stack

                if self.owner.levels.current_map.name == "cavern" and self.owner.levels.current_map.dungeon_level == 1:
                    self.owner.message_log.clear()
                    self.owner.message_log.send(
                        "A sense of impending doom fills you as you delve into the cavern.")
                    self.owner.message_log.send("RIBBIT!")

                elif self.owner.levels.current_map.name == "dream":
                    self.owner.message_log.clear()
                    self.owner.message_log.send(
                        "I'm dreaming... I feel my spirit power draining.")
                    self.owner.message_log.send("I'm hungry..")
                self.owner.render_functions.draw_messages()
                self.owner.fov_recompute = True

        elif examine:
            self.owner.game_state = GameStates.TARGETING
            cursor_component = Cursor()
            cursor = Entity(self.owner.player.x, self.owner.player.y, 4, 0xE800 + 1746, "light yellow", "cursor",
                            cursor=cursor_component, stand_on_messages=False)
            self.owner.cursor = cursor
            self.owner.levels.current_map.tiles[self.owner.cursor.x][self.owner.cursor.y].entities_on_tile.append(self.owner.cursor)
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
                self.owner.levels.current_map.tiles[prev_pos_x][prev_pos_y].entities_on_tile.remove(self.owner.cursor)
                self.owner.levels.current_map.tiles[self.owner.cursor.x][self.owner.cursor.y].entities_on_tile.append(self.owner.cursor)
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
            self.owner.levels.current_map.tiles[self.owner.cursor.x][self.owner.cursor.y].entities_on_tile.remove(self.owner.cursor)
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
                    kill_msg, self.owner.game_state = kill_player(self.owner.player)
                    self.owner.message_log.send(kill_msg)
                    self.owner.render_functions.draw_stats()
                    break

                if entity.fighter and entity.fighter.dead:
                    level_up_msg = self.owner.player.player.handle_player_exp(entity.fighter)
                    self.owner.message_log.send(kill_monster(entity))
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
                        self.owner.player, self.owner.levels.current_map, self.owner.levels.current_map.entities, self.owner.time_counter)
                    self.owner.levels.current_map.tiles[prev_pos_x][prev_pos_y].entities_on_tile.remove(entity)
                    self.owner.levels.current_map.tiles[entity.x][entity.y].entities_on_tile.append(entity)
                    if entity.occupied_tiles is not None:
                        self.owner.levels.current_map.tiles[prev_pos_x][prev_pos_y + 1].entities_on_tile.remove(entity)
                        self.owner.levels.current_map.tiles[prev_pos_x + 1][prev_pos_y + 1].entities_on_tile.remove(entity)
                        self.owner.levels.current_map.tiles[prev_pos_x + 1][prev_pos_y].entities_on_tile.remove(entity)

                        self.owner.levels.current_map.tiles[entity.x][entity.y + 1].entities_on_tile.append(entity)
                        self.owner.levels.current_map.tiles[entity.x + 1][entity.y + 1].entities_on_tile.append(entity)
                        self.owner.levels.current_map.tiles[entity.x + 1][entity.y].entities_on_tile.append(entity)

                    self.owner.fov_recompute = True
                    if combat_msg:
                        self.owner.message_log.send(combat_msg)
                        self.owner.render_functions.draw_stats()
                    if self.owner.player.fighter.dead:
                        kill_msg, self.owner.game_state = kill_player(self.owner.player)
                        self.owner.message_log.send(kill_msg)
                        self.owner.render_functions.draw_stats()
                        break
                    # Functions on monster death
                    if entity.fighter and entity.fighter.dead:
                        level_up_msg = self.owner.player.player.handle_player_exp(entity.fighter)
                        self.owner.message_log.send(kill_monster(entity))
                        self.owner.message_log.send("I feel my power returning!")
                        if level_up_msg:
                            self.owner.message_log.send(level_up_msg)
                        self.owner.fov_recompute = True

        if not self.owner.game_state == GameStates.PLAYER_DEAD:
            self.owner.game_state = GameStates.PLAYER_TURN
