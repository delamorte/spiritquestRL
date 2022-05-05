from bearlibterminal import terminal as blt
from collections import Counter

from game_states import GameStates
from helpers import get_article
from textwrap import shorten, fill
import numpy as np
from map_objects import tilemap
from scipy.spatial.distance import cityblock
from color_functions import argb_from_color
import random
from ctypes import c_uint32, addressof

from ui.message import Message


class RenderFunctions:
    def __init__(self, ui_offset_x=0, ui_offset_y=0):
        self.light_sources = None
        self.owner = None
        self.ui_offset_x = ui_offset_x
        self.ui_offset_y = ui_offset_y

    def draw(self, entity, x, y):
        if entity.hidden:
            return
        game_map = self.owner.levels.current_map
        # Draw the entity to the screen
        blt.layer(entity.layer)
        blt.color(entity.color)
        c = blt.color_from_name(entity.color)
        if not entity.cursor:
            argb = argb_from_color(c)
            a = argb[0]
            r = min(int(argb[1] * game_map.light_map[entity.x, entity.y]), 255)
            g = min(int(argb[2] * game_map.light_map[entity.x, entity.y]), 255)
            b = min(int(argb[3] * game_map.light_map[entity.x, entity.y]), 255)

            if entity.fighter and entity.status_effects.has_effect(name="invisibility"):
                a = 100
            blt.color(blt.color_from_argb(a, r, g, b))

        if not (game_map.visible[entity.x, entity.y] and
                game_map.explored[entity.x, entity.y]):
            blt.color("dark gray")

        # Cursor needs some offset in ascii
        if tilemap.data.tileset == "ascii" and entity.name == "cursor":
            blt.put_ext(x * self.owner.options.tile_offset_x, y *
                        self.owner.options.tile_offset_y, -3 * self.owner.options.tile_offset_x, -5 * self.owner.options.tile_offset_y, entity.char)
        else:
            if entity.boss and not entity.fighter:
                blt.put((x - 1) * self.owner.options.tile_offset_x, (y - 1) *
                        self.owner.options.tile_offset_y, entity.char)
            else:
                blt.put(x * self.owner.options.tile_offset_x, y *
                        self.owner.options.tile_offset_y, entity.char)

    def draw_entities(self, entities):
        game_camera = self.owner.game_camera
        player = self.owner.player
        game_map = self.owner.levels.current_map
        cursor = self.owner.cursor
        results = []
        self.light_sources = []
        for entity in entities:

            x, y = game_camera.get_coordinates(entity.x, entity.y)

            if entity.x == player.x and entity.y == player.y and entity.stand_on_messages and not entity.hidden:

                results.append(Message(get_article(
                    entity.name).capitalize() + " " + entity.colored_name + "."))
                if entity.xtra_info:
                    results.append(Message(msg=entity.xtra_info + ".", style="xtra"))

            if cursor:
                if entity.occupied_tiles is not None:
                    if (game_map.explored[entity.x, entity.y] and not entity.cursor and
                            (cursor.x, cursor.y) in entity.occupied_tiles):

                        results.append(Message(get_article(entity.name).capitalize() + " " + entity.name + "."))
                        results.append(Message(str("x: " + (str(cursor.x) + ", y: " + str(cursor.y)))))

                        if entity.xtra_info:
                            results.append(Message(msg=entity.xtra_info + ".", style="xtra"))

                        if entity.fighter:
                            self.draw_stats(entity)

                elif (entity.x == cursor.x and entity.y == cursor.y and not
                      entity.cursor and game_map.explored[entity.x, entity.y] and not entity.hidden):

                    results.append(Message(get_article(entity.name).capitalize() + " " + entity.name + "."))
                    results.append(Message(msg=str("x: " + (str(cursor.x) + ", y: " + str(cursor.y))), extend_line=True))

                    if entity.xtra_info:
                        results.append(Message(msg=entity.xtra_info + ".", style="xtra", extend_line=True))

                    if entity.fighter:
                        self.draw_stats(entity)

            if entity.name == "cursor":
                self.clear(entity, entity.last_seen_x, entity.last_seen_y)
                self.draw(entity, x, y)

            if not entity.cursor and game_map.visible[entity.x, entity.y]:
                # why is this here? causes rendering bugs!!!
                # clear(entity, entity.last_seen_x, entity.last_seen_y)

                if not entity.player and not entity.cursor:
                    entity.last_seen_x = entity.x
                    entity.last_seen_y = entity.y

                if entity.player or entity.fighter:
                    self.draw(entity, x, y)
                elif not entity.light_source:
                    self.draw(entity, x, y)
                else:
                    self.light_sources.append(entity.light_source)
                    continue

            elif (not game_map.visible[entity.x, entity.y] and
                  game_map.explored[entity.last_seen_x, entity.last_seen_y] and not
                  game_map.visible[entity.last_seen_x, entity.last_seen_y]):

                x, y = game_camera.get_coordinates(entity.last_seen_x, entity.last_seen_y)

                if entity.light_source and not entity.fighter:
                    self.light_sources.append(entity.light_source)
                else:
                    self.draw(entity, x, y)

            if game_map.visible[entity.x, entity.y] and entity.ai and self.owner.options.gfx != "ascii":
                self.draw_indicator(player)
                self.draw_indicator(entity)
                self.draw_health_bar(entity)
                self.draw_health_bar(player)
            
        self.owner.message_log.send(results)

    def draw_map(self):
        game_camera = self.owner.game_camera
        game_map = self.owner.levels.current_map
        player = self.owner.player
        # Set boundaries where to draw map
        bound_x = game_camera.bound_x * self.owner.ui.offset_x
        bound_y = game_camera.bound_y * self.owner.ui.offset_y
        bound_x2 = game_camera.bound_x2 * self.owner.ui.offset_x
        bound_y2 = game_camera.bound_y2 * self.owner.ui.offset_y
        # Clear what's drawn in camera
        self.clear_camera(6)
        # Set boundaries if map is smaller than viewport
        if game_map.width < game_camera.width:
            bound_x2 = game_map.width * self.owner.ui.offset_x
        if game_map.height < game_camera.height:
            bound_y2 = game_map.height * self.owner.ui.offset_y
        # Draw all the tiles within the boundaries of the game camera
        center = np.array([player.y, player.x])
        entities = []
        for dy, y in enumerate(range(bound_y, bound_y2, self.owner.ui.offset_y), start=1):
            for dx, x in enumerate(range(bound_x, bound_x2, self.owner.ui.offset_x), start=1):
                map_x, map_y = game_camera.x + dx, game_camera.y + dy
                if game_map.width < game_camera.width:
                    map_x = dx
                if game_map.height < game_camera.height:
                    map_y = dy
                visible = game_map.visible[map_x, map_y]

                # Draw tiles within fov
                if visible:
                    blt.layer(0)
                    if (self.owner.game_state == GameStates.TARGETING and
                            not game_map.tiles[map_x][map_y].targeting_zone and
                            self.owner.cursor.cursor.targeting_ability is not None):
                        light_level = 0.5
                    elif player.status_effects.has_effect(name="reveal") and game_map.tiles[map_x][map_y].targeting_zone:
                        light_level = 1.5
                    else:
                        dist = float(cityblock(center, np.array([map_y, map_x])))
                        light_level = game_map.tiles[map_x][map_y].natural_light_level * \
                                      (1.0 / (1.05 + 0.035 * dist + 0.025 * dist * dist))

                    if player.status_effects.has_effect(name="sneak") and game_map.tiles[map_x][map_y].targeting_zone:
                        light_level *= 0.5
                    game_map.light_map[map_x, map_y] = light_level

                    c = blt.color_from_name(game_map.tiles[map_x][map_y].color)

                    argb = argb_from_color(c)
                    a = argb[0]
                    r = min(int(argb[1] * light_level), 255)
                    g = min(int(argb[2] * light_level), 255)
                    b = min(int(argb[3] * light_level), 255)
                    blt.color(blt.color_from_argb(a, r, g, b))

                    blt.put(x, y, game_map.tiles[map_x][map_y].char)

                    if len(game_map.tiles[map_x][map_y].layers) > 0:
                        i = 1
                        for tile in game_map.tiles[map_x][map_y].layers:
                            blt.layer(i)
                            c = blt.color_from_name(tile[1])
                            argb = argb_from_color(c)
                            a = argb[0]
                            r = min(int(argb[1] * light_level), 255)
                            g = min(int(argb[2] * light_level), 255)
                            b = min(int(argb[3] * light_level), 255)
                            blt.color(blt.color_from_argb(a, r, g, b))
                            blt.put(x, y, tile[0])
                            i += 1

                # Gray out explored tiles
                elif game_map.explored[map_x, map_y]:
                    blt.layer(0)
                    blt.color("darkest gray")
                    blt.put(x, y, game_map.tiles[map_x][map_y].char)
                    if len(game_map.tiles[map_x][map_y].layers) > 0:
                        i = 1
                        for tile in game_map.tiles[map_x][map_y].layers:
                            blt.layer(i)
                            blt.put(x, y, tile[0])
                            i += 1

                if len(game_map.tiles[map_x][map_y].entities_on_tile) > 0:
                    for n in game_map.tiles[map_x][map_y].entities_on_tile:
                        if n not in entities:
                            entities.append(n)

        self.draw_entities(entities)
        if len(self.light_sources) > 0:
            self.draw_light_sources()

    def draw_light_sources(self):
        game_map = self.owner.levels.current_map
        game_camera = self.owner.game_camera
        for light in self.light_sources:
            light_fov = np.where(light.fov_map.fov)
            center = np.array([light.owner.y, light.owner.x])

            for i in range(light_fov[0].size):
                y, x = int(light_fov[0][i]), int(light_fov[1][i])
                if game_map.visible[x, y]:
                    v = np.array([y, x])
                    dist = float(cityblock(center, v))
                    light_level = game_map.tiles[x][y].natural_light_level * \
                                  (1.0 / (0.2 + 0.1 * dist + 0.025 * dist * dist))

                    if game_map.light_map[x, y] < light_level:
                        game_map.light_map[x, y] = light_level

        player_fov = np.where(game_map.visible)
        for j in range(player_fov[0].size):
            x, y = int(player_fov[0][j]), int(player_fov[1][j])
            cam_x, cam_y = game_camera.get_coordinates(x, y)
            blt.layer(0)
            c = blt.color_from_name(game_map.tiles[x][y].color)
            argb = argb_from_color(c)
            flicker = random.uniform(0.95, 1.05) if self.owner.options.flicker is True else 1
            a = argb[0]
            r = min(int(argb[1] * game_map.light_map[x, y] * flicker), 255)
            g = min(int(argb[2] * game_map.light_map[x, y] * flicker), 255)
            b = min(int(argb[3] * game_map.light_map[x, y] * flicker), 255)

            blt.color(blt.color_from_argb(a, r, g, b))
            blt.put(cam_x * self.owner.options.tile_offset_x, cam_y * self.owner.options.tile_offset_y,
                    game_map.tiles[x][y].char)

            if len(game_map.tiles[x][y].layers) > 0:
                i = 1
                for tile in game_map.tiles[x][y].layers:
                    blt.layer(i)
                    c = blt.color_from_name(tile[1])
                    argb = argb_from_color(c)
                    a = argb[0]
                    r = min(int(argb[1] * game_map.light_map[x, y] * flicker), 255)
                    g = min(int(argb[2] * game_map.light_map[x, y] * flicker), 255)
                    b = min(int(argb[3] * game_map.light_map[x, y] * flicker), 255)
                    blt.color(blt.color_from_argb(a, r, g, b))
                    blt.put(cam_x * self.owner.options.tile_offset_x, cam_y * self.owner.options.tile_offset_y,
                            tile[0])
                    i += 1

            if len(game_map.tiles[x][y].entities_on_tile) > 0:
                for entity in game_map.tiles[x][y].entities_on_tile:

                    if not entity.cursor:
                        self.clear(entity, cam_x, cam_y)
                        self.draw(entity, cam_x, cam_y)

    def draw_messages(self):
        message_log = self.owner.message_log
        msg_panel = self.owner.ui.msg_panel

        if message_log.new_msgs or not message_log.buffer:
            blt.layer(0)
            blt.clear_area(msg_panel.offset_x + msg_panel.border,
                           msg_panel.offset_y + msg_panel.border,
                           msg_panel.offset_w + msg_panel.border,
                           msg_panel.offset_h + msg_panel.border)
        if message_log.new_msgs:

            # Print the game messages, one line at a time. Display newest
            # msg at the bottom and scroll others up
            i = 5
            # if i > message_log.max_length:
            #    i = 0

            for idx, message in enumerate(message_log.buffer):

                msg = message.msg
                if message.stacked > 1:
                    msg = msg + " x{0}".format(str(message.stacked))
                blt.puts(msg_panel.border_offset, msg_panel.offset_y + msg_panel.border_offset + i * 2,
                        "[offset=0,-35]" + msg, msg_panel.offset_w - 2, 1, align=blt.TK_ALIGN_LEFT)
                i -= 1
            message_log.new_msgs = False

    def draw_stats(self, target=None):
        # TODO: Clean up this function
        player = self.owner.player
        power_msg = "[color=light azure]Spirit power left: " + str(player.player.spirit_power)
        if player.player.avatar_exp_to_spend > 0:
            power_msg = "[color=yellow]PRESS F2 TO LEVEL UP!"
        elif player.player.skill_points > 0:
            power_msg = "[color=yellow]PRESS F3 TO UPGRADE SKILLS!"

        blt.layer(0)
        blt.clear_area(2, self.owner.ui.viewport.offset_h + self.ui_offset_y + 3,
                       self.owner.ui.viewport.offset_center_x + int(len(power_msg) / 2) - 5, 3)
        blt.color("gray")

        # Draw spirit power left and position it depending on window size
        if self.owner.ui.viewport.offset_w > 90:
            blt.color("default")
            blt.puts(self.owner.ui.viewport.offset_center_x,
                     self.owner.ui.viewport.offset_h + self.ui_offset_y-1, "[offset=0,0]" + power_msg, 0, 0,
                     blt.TK_ALIGN_CENTER)
        else:
            blt.color("default")
            blt.puts(self.owner.ui.viewport.offset_w - len(power_msg),
                     self.owner.ui.viewport.offset_h + self.ui_offset_y + 1, "[offset=0,-2]" + power_msg, 0, 0,
                     blt.TK_ALIGN_LEFT)

        # Draw player stats
        if player.fighter.hp / player.fighter.max_hp < 0.34:
            hp_player = "[color=light red]HP:" + \
                        str(player.fighter.hp) + "/" + \
                        str(player.fighter.max_hp) + "  "

        else:
            hp_player = "[color=default]HP:" + \
                        str(player.fighter.hp) + "/" + \
                        str(player.fighter.max_hp) + "  "

        ev_player = "EV:" + str(player.fighter.ev) + "  "

        active_effects = []
        for x in player.status_effects.items:
            active_effects.append("[color={0}]{1} ({2} turns)".format(x.color, x.description, str(x.duration+1)))
            if x.name == "poison":
                hp_player = "[color={0}]HP:{1}/{2}  ".format(x.color, str(player.fighter.hp), str(player.fighter.max_hp))
            elif x.name == "fly":
                ev_player = "[color={0}]EV:{1}  ".format(x.color, str(player.fighter.ev))

        if active_effects:
            blt.puts(4, self.owner.ui.viewport.offset_h + self.ui_offset_y + 3,
                     "[offset=0,-2]" + "  ".join(active_effects) + "  ",
                     0, 0, blt.TK_ALIGN_LEFT)

        ac_player = "[color=default]AC:" + str(player.fighter.ac) + "  "

        power_player = "[color=default]ATK:" + str(player.fighter.atk) + "  "
        lvl_player = "LVL:" + str(player.player.char_level) + "  "
        exp_player = "EXP:" + str(player.player.char_exp["player"]) + "/" + \
                     str(player.player.char_level * player.player.exp_lvl_interval)

        blt.puts(4, self.owner.ui.viewport.offset_h + self.ui_offset_y + 1,
                 "[offset=0,-2]" + "[color=lightest green]Player:  " +
                 hp_player + ac_player + ev_player + power_player + lvl_player + exp_player,
                 0, 0, blt.TK_ALIGN_LEFT)

        # Draw target stats
        if target and not target == player:
            blt.clear_area(self.owner.ui.viewport.offset_center_x - int(len(power_msg) / 2) - 5,
                           self.owner.ui.viewport.offset_h + self.ui_offset_y + 1, self.owner.ui.viewport.offset_w, 3)

            if target.fighter.hp / target.fighter.max_hp < 0.34:
                hp_target = "[color=light red]HP:" + \
                            str(target.fighter.hp) + "/" + \
                            str(target.fighter.max_hp) + "  "
            else:
                hp_target = "[color=default]HP:" + \
                            str(target.fighter.hp) + "/" + \
                            str(target.fighter.max_hp) + "  "

            ev_target = "EV:" + str(target.fighter.ev) + "  "
            active_effects = []
            for x in target.status_effects.items:
                if x.duration > 0:
                    active_effects.append("[color={0}]{1} ({2})".format(x.color, x.description, str(x.duration+1)))
                    if x.name == "poison":
                        hp_target = "[color={0}]HP:{1}/{2}  ".format(x.color, str(target.fighter.hp), str(target.fighter.max_hp))
                    elif x.name == "fly":
                        ev_target = "[color={0}]EV:{1}  ".format(x.color, str(target.fighter.ev))

            if active_effects:
                blt.puts(self.owner.ui.viewport.offset_w, self.owner.ui.viewport.offset_h + self.ui_offset_y + 3,
                         "[offset=0,-2]" + "  ".join(active_effects) + "  ",
                         0, 0, blt.TK_ALIGN_RIGHT)

            ac_target = "[color=default]AC:" + str(target.fighter.ac) + "  "
            power_target = "ATK:" + str(target.fighter.atk) + " "

            blt.puts(self.owner.ui.viewport.offset_w-1, self.owner.ui.viewport.offset_h + self.ui_offset_y + 1,
                     "[offset=0,-2]" + target.colored_name + ":  " + hp_target + ac_target + ev_target + power_target,
                     0, 0, blt.TK_ALIGN_RIGHT)

            if target.fighter.hp <= 0:
                blt.clear_area(2, self.owner.ui.viewport.offset_h +
                               self.ui_offset_y + 1, self.owner.ui.viewport.offset_w, 3)

    def draw_ui(self, element):
        self.clear_camera(element.w, element.h, 5)
        blt.color(element.color)
        blt.layer(6)

        for x in range(element.offset_x+1, element.offset_x2):
            blt.put(x, element.offset_y, element.tile_horizontal)
            blt.put(x, element.offset_y2, element.tile_horizontal)
            if x == element.offset_x + 1:
                blt.put(x, element.offset_y, element.tile_nw)
                blt.put(x, element.offset_y2, element.tile_sw)
            elif x == element.offset_x2 - 1:
                blt.put(x, element.offset_y, element.tile_ne)
                blt.put(x, element.offset_y2, element.tile_se)

        for y in range(element.offset_y+2, element.offset_y2-1):
            blt.put(element.offset_x, y, element.tile_vertical)
            blt.put(element.offset_x2, y, element.tile_vertical)

    def draw_indicator(self, entity):
        # Draw player indicator
        blt.layer(4)
        x, y = self.owner.game_camera.get_coordinates(entity.x, entity.y)
        blt.color(entity.indicator_color)
        if entity.occupied_tiles is not None:
            return
        else:
            blt.put(x * self.owner.options.tile_offset_x, y *
                    self.owner.options.tile_offset_y, tilemap.data.tiles["indicator"])

        if entity.ai and entity.ai.cant_see_player:
            blt.color(None)
            blt.put_ext(x * self.owner.options.tile_offset_x + 2, y *
                        self.owner.options.tile_offset_y, 5, -5, '?')

    def draw_health_bar(self, entity):
        blt.layer(4)
        x, y = self.owner.game_camera.get_coordinates(entity.x, entity.y)
        full_hp = "[color=green].[color=green].[color=green].[color=green]."
        three_q_hp = "[color=green].[color=green].[color=green].[color=red]."
        half_hp = "[color=green].[color=green].[color=red].[color=red]."
        one_q_hp = "[color=green].[color=red].[color=red].[color=red]."
        zero_hp = "[color=red].[color=red].[color=red].[color=red]."

        if entity.fighter.hp <= 0:
            hp_bar = zero_hp
        elif entity.fighter.hp / entity.fighter.max_hp <= 0.25:
            hp_bar = one_q_hp
        elif entity.fighter.hp / entity.fighter.max_hp <= 0.5:
            hp_bar = half_hp
        elif entity.fighter.hp / entity.fighter.max_hp <= 0.75:
            hp_bar = three_q_hp
        else:
            hp_bar = full_hp

        blt.puts(x * self.owner.options.tile_offset_x, y * self.owner.options.tile_offset_y + 2, hp_bar)

    def draw_minimap(self):
        blt.layer(1)
        x0 = self.owner.ui.side_panel.offset_x
        y0 = self.owner.ui.side_panel.offset_y
        game_map = self.owner.levels.current_map

        minimap = np.ones_like(game_map.tiles, dtype=int)
        for x in range(game_map.width):
            for y in range(game_map.height):
                visible = game_map.visible[x, y]
                if visible:
                    minimap[y][x] = blt.color_from_name("dark gray")
                    if len(game_map.tiles[x][y].entities_on_tile) > 0:
                        if game_map.tiles[x][y].entities_on_tile[-1].name == "tree":
                            minimap[y][x] = blt.color_from_name("dark green")
                        elif "wall" in game_map.tiles[x][y].entities_on_tile[-1].name:
                            minimap[y][x] = blt.color_from_name("dark amber")
                        elif game_map.tiles[x][y].entities_on_tile[-1].name == "player":
                            minimap[y][x] = blt.color_from_name(None)
                        elif game_map.tiles[x][y].entities_on_tile[-1].fighter \
                                and game_map.tiles[x][y].entities_on_tile[-1].name != "player":
                            minimap[y][x] = blt.color_from_name("light red")
                        else:
                            minimap[y][x] = blt.color_from_name("light gray")
                    elif game_map.tiles[x][y].blocked:
                        minimap[y][x] = blt.color_from_name("light gray")
                elif game_map.explored[x, y]:
                    if len(game_map.tiles[x][y].entities_on_tile) > 0:
                        minimap[y][x] = blt.color_from_name("light gray")
                    else:
                        minimap[y][x] = blt.color_from_name("dark gray")

        minimap = minimap.flatten()
        minimap = (c_uint32 * len(minimap))(*minimap)

        blt.set(
            "U+F900: %d, raw-size=%dx%d, resize=%dx%d, resize-filter=nearest" % (
                addressof(minimap),
                game_map.width, game_map.height,
                200, 240)
        )

        blt.put(x0 + 3, y0 + 3, 0xF900)

    def draw_animations(self):
        # num_of_animations = len(self.owner.animations_buffer)
        game_map = self.owner.levels.current_map
        for animation in self.owner.animations_buffer:

            if (animation.target.dead or animation.target.fighter is None or animation.target.dead or not
                    animation.target.visible):
                self.owner.animations_buffer.remove(animation)
                continue
            elif (animation.owner.dead or animation.owner.fighter is None or animation.owner.dead or not
                    animation.owner.visible):
                self.owner.animations_buffer.remove(animation)
                continue

            if animation.cached_alpha is None:
                self.owner.animations_buffer.remove(animation)
                continue

            for i, alpha in enumerate(animation.cached_alpha):
                # avoid blocking animation rendering with blt.read
                if blt.has_input():
                    key = blt.read()
                    # if animation interrupted by key press, cache rest of the frames
                    animation.cached_alpha = animation.cached_alpha[i:]
                    if animation.dialog is None:
                        # Dialog doesn't have frame buffer
                        animation.cached_frames = animation.cached_frames[i:]
                    return key
                visible = game_map.visible[animation.target.x, animation.target.y]
                if visible:
                    x, y = self.owner.game_camera.get_coordinates(animation.target.x, animation.target.y)
                    blt.layer(4)
                    c = blt.color_from_name(animation.color)
                    argb = argb_from_color(c)
                    a, r, g, b = alpha.item(), argb[1], argb[2], argb[3]
                    blt.color(blt.color_from_argb(a, r, g, b))

                    if animation.dialog is not None:
                        blt.puts(x * self.owner.options.tile_offset_x - 13, y *
                                 self.owner.options.tile_offset_y - 2,
                                 animation.dialog, 30, 0, blt.TK_ALIGN_CENTER+blt.TK_ALIGN_MIDDLE)
                    else:
                        blt.put_ext(x * self.owner.options.tile_offset_x, y *
                                    self.owner.options.tile_offset_y, animation.offset_x, animation.offset_y,
                                    animation.cached_frames[i].item())
                    blt.refresh()
                # remove cache if animation finished
                if i == animation.cached_alpha.size - 1:
                    animation.cached_alpha = None
                    if animation.dialog is None:
                        # Dialog doesn't have frame buffer
                        animation.cached_frames = None
                    animation.dialog = None

            if animation.cached_alpha is None:
                # remove from buffer after all frames rendered
                self.owner.animations_buffer.remove(animation)
        return None

    def draw_turn_count(self):
        x = self.owner.ui.side_panel.offset_x + self.owner.ui.side_panel.x_margin
        y = self.owner.ui.side_panel.offset_y + 26
        blt.layer(1)
        blt.color(None)
        blt.clear_area(x, y, self.owner.ui.side_panel.offset_w - self.owner.ui.side_panel.x_margin, 1)
        blt.puts(x, y, "Turn: " + str(self.owner.time_counter.turn), 0, 0,
                 blt.TK_ALIGN_LEFT)

    def draw_side_panel_content(self):
        game_map = self.owner.levels.current_map
        player = self.owner.player
        side_panel = self.owner.ui.side_panel
        # Draw side panel content
        blt.layer(1)
        blt.color(None)
        x_margin = self.owner.ui.side_panel.x_margin
        map_title = fill(game_map.title, 21)

        blt.clear_area(side_panel.offset_x + x_margin,
                       side_panel.offset_y + 20,
                       side_panel.offset_w - x_margin,
                       side_panel.offset_h - 40)

        blt.puts(side_panel.offset_x + x_margin,
                 side_panel.offset_y + 21, "Location: " + map_title, 0, 0,
                 blt.TK_ALIGN_LEFT)
        blt.puts(side_panel.offset_x + x_margin,
                 side_panel.offset_y + 24 + map_title.count('\n'), "World tendency: " +
                 str(self.owner.levels.world_tendency), 0, 0, blt.TK_ALIGN_LEFT)

        # Fetch player skills and draw icons
        weapon = []
        attack = []
        utility = []
        for skill in player.abilities.items:
            if skill.skill_type == "weapon":
                weapon.append(skill)
            elif skill.skill_type == "attack":
                attack.append(skill)
            elif skill.skill_type == "utility":
                utility.append(skill)

        blt.color(None)

        # Weapon skills
        y_margin = 0
        first_heading_y = 30
        fill_chars = 32
        for i, wpn in enumerate(weapon):
            if wpn.name == player.player.sel_weapon.name:
                # heading
                title = "Weapon (Switch: 'W')"
                blt.color("lighter yellow")
                blt.puts(side_panel.offset_x + x_margin,
                         side_panel.offset_y + first_heading_y, fill(title, fill_chars), 0, 0,
                         blt.TK_ALIGN_LEFT)

                # name of the selected skill
                blt.color(None)
                skill_str = "{0}, {1}+{2} dmg".format(wpn.name.capitalize(), wpn.damage[wpn.rank], player.fighter.str_bonus)
                blt.puts(side_panel.offset_x + x_margin,
                         side_panel.offset_y + first_heading_y + 2, fill(skill_str, fill_chars), 0, 0,
                         blt.TK_ALIGN_LEFT)

                # highlight icon of the selected skill
                blt.color("dark amber")
                y_margin += skill_str.count('\n')

            if i > 4:
                y_margin += 3
                i = 0

            blt.put(side_panel.offset_x + x_margin + 1 + i * 6,
                    side_panel.offset_y + first_heading_y + 4, wpn.icon)
            blt.color(None)

        second_heading_y = first_heading_y + 9

        # Attack skills
        for i, atk in enumerate(attack):

            if player.player.sel_attack and atk.name == player.player.sel_attack.name:
                # heading
                title = "Skills (Switch: 'A', Use: 'TAB')"
                blt.color("lighter green")
                blt.puts(side_panel.offset_x + x_margin,
                         side_panel.offset_y + second_heading_y + y_margin,
                         fill(title, fill_chars), 0, 0,
                         blt.TK_ALIGN_LEFT)

                blt.color(None)
                skill_str = "{0}: ".format(atk.name)
                chance_str, atk_str, effect_str, duration_str = "", "", "", ""
                if atk.chance:
                    # chance_str = str(int(1 / atk.chance[atk.rank])) + "% chance of "
                    chance_str = "100% chance of "
                if atk.effect:
                    effect_str = ", ".join(atk.effect) + ", "
                if atk.duration:
                    duration_str = atk.duration[atk.rank] + " turns"
                if atk.damage:
                    atk_str = ", " + atk.damage[atk.rank] + "+" + str(player.fighter.str_bonus) + " dmg" if duration_str \
                        else atk.damage[atk.rank] + "+" + str(player.fighter.str_bonus) + " dmg"
                skill_str += chance_str + effect_str + duration_str + atk_str

                blt.puts(side_panel.offset_x + x_margin,
                         side_panel.offset_y + second_heading_y + 2 + y_margin,
                         fill(skill_str.capitalize(), fill_chars), 0, 0,
                         blt.TK_ALIGN_LEFT)
                # highlight icon of the selected skill
                blt.color("dark amber")
                y_margin += skill_str.count('\n')

            if i > 4:
                y_margin += 3
                i = 0

            blt.put(side_panel.offset_x + x_margin + 1 + i * 6,
                    side_panel.offset_y + second_heading_y + 5 + y_margin, atk.icon)
            blt.color(None)

        third_heading_y = second_heading_y + 10

        # Utility skills
        for i, utl in enumerate(utility):
            if player.player.sel_utility and utl.name == player.player.sel_utility.name:
                title = "Utility (Use: 'Z')"
                blt.color("lighter blue")
                blt.puts(side_panel.offset_x + x_margin,
                         side_panel.offset_y + third_heading_y + y_margin,
                         fill(title, fill_chars),
                         0, 0, blt.TK_ALIGN_LEFT)

                # name of the selected skill
                blt.color(None)
                skill_str = utl.name
                blt.puts(side_panel.offset_x + x_margin,
                         side_panel.offset_y + third_heading_y + 2 + y_margin,
                         fill(skill_str.capitalize(), fill_chars),
                         0, 0, blt.TK_ALIGN_LEFT)
                y_margin += skill_str.count('\n')
                blt.puts(side_panel.offset_x + x_margin,
                         side_panel.offset_y + third_heading_y + 8 + y_margin,
                         fill(utl.description.capitalize(), fill_chars), 46 + y_margin, 0,
                         blt.TK_ALIGN_LEFT)
                # highlight icon of the selected skill
                blt.color("dark amber")

            if i > 4:
                y_margin += 3
                i = 0

            blt.put(side_panel.offset_x + x_margin + 1 + i * 6,
                    side_panel.offset_y + third_heading_y + 5 + y_margin, utl.icon)
            blt.layer(0)
            blt.put_ext(side_panel.offset_x + x_margin + i * 6,
                    side_panel.offset_y + third_heading_y + 5 + y_margin, -2, -14, str(i+1))
            blt.layer(1)
            blt.color(None)

    def draw_all(self):
        player = self.owner.player
        game_map = self.owner.levels.current_map
        game_camera = self.owner.game_camera
        game_camera.move_camera(player.x, player.y, game_map.width, game_map.height)

        self.draw_map()
        self.draw_stats()
        self.draw_minimap()

    def clear(self, entity, x, y):
        # Clear the entity from the screen
        blt.layer(entity.layer)
        blt.clear_area(x * self.owner.options.tile_offset_x, y *
                       self.owner.options.tile_offset_y, 1, 1)
        if entity.boss:
            blt.clear_area(x * self.owner.options.tile_offset_x, y *
                           self.owner.options.tile_offset_y, 2, 2)

    def clear_camera(self, n, w=None, h=None):
        if not w:
            w = self.owner.ui.viewport.offset_w
        if not h:
            h = self.owner.ui.viewport.offset_h
        i = 0
        while i < n:
            blt.layer(i)
            blt.clear_area(1, 1, w, h)
            i += 1
