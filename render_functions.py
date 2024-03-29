from ctypes import c_uint32, addressof
from textwrap import fill

import numpy as np
from bearlibterminal import terminal as blt
from scipy.spatial.distance import chebyshev

import options
from color_functions import argb_from_color
from game_states import GameStates
from helpers import get_article
from map_gen.tilemap import get_color
from ui.message import Message


def get_light_adjusted_color(game_map, x, y, direction=None, cardinal=None, get_color_from=None):
    if cardinal is not None and direction and game_map.tiles[x][y].corners:
        if cardinal == 0 or cardinal == 2:
            directions_to_corners = {
                "nw": 1,
                "sw": 0,
                "se": 3,
                "ne": 2,
            }
        else:
            directions_to_corners = {
                "nw": 3,
                "sw": 2,
                "se": 1,
                "ne": 0,
            }
        corner_idx = directions_to_corners[direction]
        return game_map.tiles[x][y].corners[corner_idx]
    if game_map.tiles[x][y].corners and direction:
        directions_to_corners = {
            "nw": 2,
            "sw": 3,
            "se": 0,
            "ne": 1,
        }
        corner_idx = directions_to_corners[direction]
        return game_map.tiles[x][y].corners[corner_idx]

    # if game_map.tiles[x][y].light_adjusted_color and not get_color_from:
    #     return game_map.tiles[x][y].light_adjusted_color
    if get_color_from:
        c = blt.color_from_name(game_map.tiles[get_color_from[0]][get_color_from[1]].color)
    else:
        c = blt.color_from_name(game_map.tiles[x][y].color)

    argb = argb_from_color(c)
    a = argb[0]
    r = min(int(argb[1] * game_map.light_map[x, y]), 255)
    g = min(int(argb[2] * game_map.light_map[x, y]), 255)
    b = min(int(argb[3] * game_map.light_map[x, y]), 255)

    light_adjusted_color = blt.color_from_argb(a, r, g, b)

    return light_adjusted_color


def get_light_adjusted_corners(game_map, x, y, cardinal=None):
    corners = []
    room_id = game_map.tiles[x][y].room_id
    get_color_from = None

    if cardinal is not None:
        if cardinal == 0 or cardinal == 2:
            directions = {
                "nw": (x, y - 1),
                "sw": (x, y + 1),
                "se": (x, y + 1),
                "ne": (x, y - 1),
            }
        else:
            directions = {
                "nw": (x - 1, y),
                "sw": (x - 1, y),
                "se": (x + 1, y),
                "ne": (x + 1, y),
            }
    else:
        directions = {
            "nw": (x - 1, y - 1),
            "sw": (x - 1, y + 1),
            "se": (x + 1, y + 1),
            "ne": (x + 1, y - 1),
        }

    for direction, coords in directions.items():
        x2, y2 = coords[0], coords[1]
        if game_map.tiles[x2][
            y2].room_id != room_id or x2 >= game_map.width or x2 <= 0 or y2 >= game_map.height or y2 <= 0:
            get_color_from = (x, y)
        color = get_light_adjusted_color(game_map, x2, y2, direction, cardinal, get_color_from)
        corners.append(color)

    return corners


class RenderFunctions:
    def __init__(self, ui_offset_x=0, ui_offset_y=0):
        self.light_sources = None
        self.owner = None
        self.ui_offset_x = ui_offset_x
        self.ui_offset_y = ui_offset_y

    def draw(self, entity, x, y):
        if (x <= 0 or y <= 0 or x * options.data.tile_offset_x > self.owner.ui.viewport.offset_x2 or y *
                options.data.tile_offset_y > self.owner.ui.viewport.offset_y2):
            return
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
            light_level = game_map.light_map[entity.x, entity.y]
            r = min(int(argb[1] * light_level), 255)
            g = min(int(argb[2] * light_level), 255)
            b = min(int(argb[3] * light_level), 255)

            if entity.fighter and entity.status_effects.has_effect(name="invisibility"):
                a = 100
            blt.color(blt.color_from_argb(a, r, g, b))

        if not (game_map.visible[entity.x, entity.y] and
                game_map.explored[entity.x, entity.y]):
            blt.color("dark gray")

        # Cursor needs some offset in ascii
        if options.data.gfx == "ascii" and entity.name == "cursor":
            blt.put_ext(x * options.data.tile_offset_x, y *
                        options.data.tile_offset_y, -3 * options.data.tile_offset_x, -5 * options.data.tile_offset_y,
                        entity.char)
        else:
            if entity.boss and not entity.fighter:
                blt.put((x - 1) * options.data.tile_offset_x, (y - 1) *
                        options.data.tile_offset_y, entity.char)
            else:
                blt.put(x * options.data.tile_offset_x, y *
                        options.data.tile_offset_y, entity.char)

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
                    results.append(
                        Message(msg=str("x: " + (str(cursor.x) + ", y: " + str(cursor.y))), extend_line=True))
                    results.append(Message(str(", color: " + entity.color), extend_line=True))
                    results.append(Message(str(", layer: " + str(entity.layer)), extend_line=True))
                    results.append(
                        Message(str(", light: " + str(game_map.light_map[entity.x, entity.y])), extend_line=True))
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

            if entity.xtra_info and game_map.visible[entity.x, entity.y] and \
                    not entity.x == player.x and not entity.y == player.y:
                results.append(Message(msg=entity.xtra_info + ".", style="xtra"))
                entity.xtra_info = None

            if game_map.visible[entity.x, entity.y] and entity.ai and options.data.gfx != "ascii":
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
        self.clear_camera(3)
        # Set boundaries if map is smaller than viewport
        if game_map.width < game_camera.width:
            bound_x2 = game_map.width * self.owner.ui.offset_x
        if game_map.height < game_camera.height:
            bound_y2 = game_map.height * self.owner.ui.offset_y
        # Draw all the tiles within the boundaries of the game camera
        entities = []
        map_xy = []
        for dy, y in enumerate(range(bound_y, bound_y2, self.owner.ui.offset_y), start=1):
            for dx, x in enumerate(range(bound_x, bound_x2, self.owner.ui.offset_x), start=1):
                map_x, map_y = game_camera.x + dx, game_camera.y + dy
                map_xy.append((map_x, map_y))
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
                    elif player.status_effects.has_effect(name="reveal") and game_map.tiles[map_x][
                        map_y].targeting_zone:
                        light_level = 1.5
                    else:
                        light_level = 1.5
                        # dist = float(chebyshev(center, np.array([map_y, map_x])))
                        # light_level = game_map.tiles[map_x][map_y].natural_light_level * \
                        #               (1.0 / (1.05 + 0.035 * dist + 0.015 * dist * dist))

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

                # Gray out explored tiles
                elif game_map.explored[map_x, map_y]:
                    blt.layer(0)
                    blt.color("darkest gray")
                    blt.put(x, y, game_map.tiles[map_x][map_y].char)

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

            light.recompute_fov(game_map)
            light_fov = np.where(light.fov_map)
            center = np.array([light.owner.y, light.owner.x])

            for j in range(light_fov[0].size):
                x, y = int(light_fov[0][j]), int(light_fov[1][j])
                if light.fov_map[x, y]:
                    if light.lit:
                        v = np.array([y, x])
                        dist = float(chebyshev(center, v))
                        light_level = game_map.tiles[x][y].natural_light_level * \
                                      (1.5 / (0.3 + 0.1 * dist + 0.010 * dist))

                        if game_map.light_map[x, y] < light_level:
                            game_map.light_map[x, y] = light_level
                    else:
                        game_map.tiles[x][y].light_adjusted_color = None
                        game_map.tiles[x][y].corners = None

        player_fov = np.where(game_map.visible)
        for j in range(player_fov[0].size):
            x, y = int(player_fov[0][j]), int(player_fov[1][j])
            cam_x, cam_y = game_camera.get_coordinates(x, y)
            if len(game_map.tiles[x][y].entities_on_tile) > 0:
                for entity in game_map.tiles[x][y].entities_on_tile:

                    if not entity.cursor:
                        self.clear(entity, cam_x, cam_y)
                        self.draw(entity, cam_x, cam_y)
            if game_map.light_map[x, y] == 1.5:
                continue
            blt.layer(0)

            light_adjusted_color = get_light_adjusted_color(game_map, x, y)
            game_map.tiles[x][y].light_adjusted_color = light_adjusted_color

            blt.color(light_adjusted_color)

            blt.put(cam_x * options.data.tile_offset_x, cam_y * options.data.tile_offset_y,
                    game_map.tiles[x][y].char)

        blt.layer(0)

        for light in self.light_sources:
            if not light.lit:
                continue
            x, y = light.owner.x, light.owner.y
            game_map.tiles[x][y].corners = None
            room_id = game_map.tiles[x][y].room_id
            for i in range(1, light.radius + 1):
                nw = (x - i, y - i)
                sw = (x - i, y + i)
                se = (x + i, y + i)
                ne = (x + i, y - i)

                for corner in [nw, sw, se, ne]:
                    x2, y2 = corner[0], corner[1]
                    if x2 >= game_map.width or x2 <= 0 or y2 >= game_map.height or y2 <= 0:
                        continue
                    if not game_map.visible[x2, y2] or game_map.tiles[x2][y2].room_id != room_id:
                        continue
                    skip_tile = False
                    if game_map.tiles[x2][y2].entities_on_tile:
                        for entity in game_map.tiles[x2][y2].entities_on_tile:
                            if entity.light_source and entity.light_source.lit:
                                skip_tile = True
                                break
                    if skip_tile:
                        continue

                    corners = get_light_adjusted_corners(game_map, x2, y2)

                    cam_x, cam_y = game_camera.get_coordinates(x2, y2)
                    blt.put_ext(cam_x * options.data.tile_offset_x, cam_y * options.data.tile_offset_y, 0, 0,
                                game_map.tiles[x2][y2].char, corners)
                    game_map.tiles[x2][y2].corners = corners

                try:
                    n = game_map.tiles[x - i + 1:x + i, y - i]
                except IndexError as err:
                    n = None
                try:
                    w = game_map.tiles[x - i, y - i + 1:y + i]
                except IndexError as err:
                    w = None
                try:
                    s = game_map.tiles[x - i + 1:x + i, y + i]
                except IndexError as err:
                    s = None
                try:
                    e = game_map.tiles[x + i, y - i + 1:y + i]
                except IndexError as err:
                    e = None

                for idx, cardinal in enumerate([n, w, s, e]):
                    if cardinal is None:
                        continue
                    for tile in cardinal:
                        x2, y2 = tile.x, tile.y
                        if not game_map.visible[x2, y2] or game_map.tiles[x2][y2].room_id != room_id:
                            continue
                        if x2 >= game_map.width or x2 <= 0 or y2 >= game_map.height or y2 <= 0:
                            continue
                        skip_tile = False
                        if game_map.tiles[x2][y2].entities_on_tile:
                            for entity in game_map.tiles[x2][y2].entities_on_tile:
                                if entity.light_source and entity.light_source.lit:
                                    skip_tile = True
                                    break
                        if skip_tile:
                            continue
                        corners = get_light_adjusted_corners(game_map, x2, y2, cardinal=idx)

                        cam_x, cam_y = game_camera.get_coordinates(x2, y2)
                        blt.put_ext(cam_x * options.data.tile_offset_x, cam_y * options.data.tile_offset_y, 0, 0,
                                    game_map.tiles[x2][y2].char, corners)
                        game_map.tiles[x2][y2].corners = corners

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
                     self.owner.ui.viewport.offset_h + self.ui_offset_y - 1, "[offset=0,0]" + power_msg, 0, 0,
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
            active_effects.append("[color={0}]{1} ({2} turns)".format(x.color, x.description, str(x.duration + 1)))
            if x.name == "poison":
                hp_player = "[color={0}]HP:{1}/{2}  ".format(x.color, str(player.fighter.hp),
                                                             str(player.fighter.max_hp))
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
                    active_effects.append("[color={0}]{1} ({2})".format(x.color, x.description, str(x.duration + 1)))
                    if x.name == "poison":
                        hp_target = "[color={0}]HP:{1}/{2}  ".format(x.color, str(target.fighter.hp),
                                                                     str(target.fighter.max_hp))
                    elif x.name == "fly":
                        ev_target = "[color={0}]EV:{1}  ".format(x.color, str(target.fighter.ev))

            if active_effects:
                blt.puts(self.owner.ui.viewport.offset_w, self.owner.ui.viewport.offset_h + self.ui_offset_y + 3,
                         "[offset=0,-2]" + "  ".join(active_effects) + "  ",
                         0, 0, blt.TK_ALIGN_RIGHT)

            ac_target = "[color=default]AC:" + str(target.fighter.ac) + "  "
            power_target = "ATK:" + str(target.fighter.atk) + " "

            blt.puts(self.owner.ui.viewport.offset_w - 1, self.owner.ui.viewport.offset_h + self.ui_offset_y + 1,
                     "[offset=0,-2]" + target.colored_name + ":  " + hp_target + ac_target + ev_target + power_target,
                     0, 0, blt.TK_ALIGN_RIGHT)

            if target.fighter.hp <= 0:
                blt.clear_area(2, self.owner.ui.viewport.offset_h +
                               self.ui_offset_y + 1, self.owner.ui.viewport.offset_w, 3)

    def draw_ui(self, element):
        self.clear_camera(1, element.w, element.h)
        blt.color(element.owner.color)
        blt.layer(2)

        for x in range(element.offset_x + 1, element.offset_x2):
            blt.put(x, element.offset_y, element.owner.tile_horizontal)
            blt.put(x, element.offset_y2, element.owner.tile_horizontal)
            if x == element.offset_x + 1:
                blt.put(x, element.offset_y, element.owner.tile_nw)
                blt.put(x, element.offset_y2, element.owner.tile_sw)
            elif x == element.offset_x2 - 1:
                blt.put(x, element.offset_y, element.owner.tile_ne)
                blt.put(x, element.offset_y2, element.owner.tile_se)

        for y in range(element.offset_y + 2, element.offset_y2 - 1):
            blt.put(element.offset_x, y, element.owner.tile_vertical)
            blt.put(element.offset_x2, y, element.owner.tile_vertical)

    def draw_indicator(self, entity):
        # Draw player indicator
        blt.layer(3)
        x, y = self.owner.game_camera.get_coordinates(entity.x, entity.y)
        blt.color(entity.indicator_color)
        blt.put(x * options.data.tile_offset_x, y *
                options.data.tile_offset_y, options.data.indicator)

        if entity.ai and entity.ai.cant_see_player:
            blt.color(None)
            blt.put_ext(x * options.data.tile_offset_x + 2, y *
                        options.data.tile_offset_y, 5, -5, '?')

    def draw_health_bar(self, entity):
        blt.layer(1)
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

        if entity.occupied_tiles is not None:
            offset_y = 3
            offset_x = 2
        else:
            offset_y = 0
            offset_x = 0

        blt.puts(x * options.data.tile_offset_x + offset_x, y * options.data.tile_offset_y + 2 + offset_y, hp_bar)

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

    def draw_debug_map(self, params=None, blank_map=True):
        if blank_map:
            # parse level generator name from params, generate & draw new map
            game_map = self.owner.levels.make_debug_map(algorithm=params)
        elif params:
            game_map = params
        else:
            game_map = self.owner.levels.current_map

        blt.clear()
        blt.layer(4)
        x0 = 4
        y0 = 3

        for x in range(game_map.width):
            for y in range(game_map.height):
                color = get_color(game_map.biome.biome_data["floor"])
                blt.color(color)
                blt.layer(4)
                blt.put(x0 + x * 2, y0 + y, game_map.tiles[x][y].char)

                for i, room in enumerate(game_map.algorithm.rooms):
                    if (x, y) in room.inner:
                        # blt.color(room.id_color)
                        blt.color(game_map.tiles[x][y].color)

                        blt.layer(4)
                        blt.put(x0 + x * 2, y0 + y, game_map.tiles[x][y].char)

                if len(game_map.tiles[x][y].entities_on_tile) > 0:
                    for entity in game_map.tiles[x][y].entities_on_tile:
                        blt.layer(6)
                        blt.color(entity.color)
                        blt.put(x0 + x * 2, y0 + y, entity.char)
                        # if game_map.tiles[x][y].entities_on_tile[-1].name == "player":
                        #     blt.color("green")
                        #     blt.put(x0 + x * 2, y0 + y, "@")

                # draw room id and feature name
                for room in game_map.algorithm.rooms:
                    random_point = next(iter(room.inner))
                    if x == random_point[0] and y == random_point[1]:
                        print("Room: {0}, x1: {1}, y1: {2}, size: {3}, algorithm: {4}".format(room.feature, room.x1,
                                                                                              room.y1,
                                                                                              room.nd_array.size,
                                                                                              room.algorithm))
                        blt.color(None)
                        blt.layer(7)
                        blt.puts(x0 + x * 2, y0 + y, "{0}: {1}".format(room.id_nr, room.feature))
                        # blt.puts(x0 + x*2, y0 + y + 1, "{0}".format(room.feature))
                        break
        return

    def draw_animations(self):
        game_map = self.owner.levels.current_map
        frames_length = 0
        for item in self.owner.animations_buffer:
            if item.cached_alpha is not None:
                length = len(item.cached_alpha)
                if length > frames_length:
                    frames_length = length
            else:
                self.owner.animations_buffer.remove(item)

        for i in range(frames_length):
            if not self.owner.animations_buffer:
                return None

            for animation in self.owner.animations_buffer:

                # avoid blocking game while rendering with blt.read
                if blt.has_input():
                    key = blt.read()
                    # if animation interrupted by key press, cache rest of the frames
                    if animation.cached_alpha is not None and animation.cached_alpha.size > 0:
                        animation.cached_alpha = animation.cached_alpha[i:]
                    if animation.dialog is None and animation.cached_frames is not None:
                        # Dialog doesn't have frame buffer
                        animation.cached_frames = animation.cached_frames[i:]
                    return key

                if (animation.target.dead or animation.target.fighter is None or animation.target.dead or not
                animation.target.visible):
                    animation.finish(self.owner.animations_buffer)
                    continue
                elif (animation.owner.dead or animation.owner.fighter is None or animation.owner.dead or not
                animation.owner.visible):
                    animation.finish(self.owner.animations_buffer)
                    continue

                if animation.cached_alpha is None:
                    animation.finish(self.owner.animations_buffer)
                    continue

                if i >= len(animation.cached_alpha):
                    break

                visible = game_map.visible[animation.target.x, animation.target.y]
                if visible:
                    x, y = self.owner.game_camera.get_coordinates(animation.target.x, animation.target.y)
                    blt.layer(3)
                    c = blt.color_from_name(animation.color)
                    argb = argb_from_color(c)
                    try:
                        a, r, g, b = animation.cached_alpha[i].item(), argb[1], argb[2], argb[3]
                    except IndexError as e:
                        print(e)
                        break

                    # Avoid drawing animation if frame and position haven't changed
                    if (i > 0 and animation.cached_alpha[i] == animation.cached_alpha[i - 1] and
                            animation.single_frame and animation.target.x == animation.target.last_seen_x and
                            animation.target.y == animation.target.last_seen_y):
                        continue

                    blt.color(blt.color_from_argb(a, r, g, b))

                    if animation.dialog is not None:
                        if animation.target.x > game_map.width - 5 or animation.target.x < 5:
                            continue
                        offset = -2
                        if animation.target.y == 1:
                            offset = 1
                        blt.puts(x * options.data.tile_offset_x - 13, y *
                                 options.data.tile_offset_y + offset,
                                 animation.dialog, 30, 0, blt.TK_ALIGN_CENTER + blt.TK_ALIGN_MIDDLE)
                    elif animation.cached_frames is not None:
                        blt.put_ext(x * options.data.tile_offset_x, y *
                                    options.data.tile_offset_y, animation.offset_x, animation.offset_y,
                                    animation.cached_frames[i].item())

                    # remove cache if animation finished
                    if i == animation.cached_alpha.size - 1:
                        animation.cached_alpha = None
                        if animation.dialog is None:
                            # Dialog doesn't have frame buffer
                            animation.cached_frames = None
                        animation.dialog = None

                if animation.cached_alpha is None:
                    # remove from buffer after all frames rendered
                    animation.finish(self.owner.animations_buffer)

            blt.refresh()
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
                skill_str = "{0}, {1}+{2} dmg".format(wpn.name.capitalize(), wpn.damage[wpn.rank],
                                                      player.fighter.str_bonus)
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
                    if atk.rank >= len(atk.damage):
                        damage = atk.damage[-1]
                    else:
                        damage = atk.damage[atk.rank]
                    atk_str = ", " + damage + "+" + str(player.fighter.str_bonus) + " dmg" if (
                        duration_str) \
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

        third_heading_y = second_heading_y + 10 if attack else second_heading_y

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
            blt.put_ext(side_panel.offset_x + x_margin + i * 6,
                        side_panel.offset_y + third_heading_y + 5 + y_margin, -2, -14, str(i + 1))
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
        blt.clear_area(x * options.data.tile_offset_x, y *
                       options.data.tile_offset_y, 1, 1)
        if entity.boss:
            blt.clear_area(x * options.data.tile_offset_x, y *
                           options.data.tile_offset_y, 2, 2)

    def clear_camera(self, n, w=None, h=None):
        """
        Clears all entities in n layers from blt camera area.
        Layers:
        0 - background, ground tiles
        1 - objects, ui
        2 - player
        3 - overlay elements, such as animations and indicator icons
        :param n: numbers of layers to clear
        :param w: width of area to clear
        :param h: height of area to clear
        """
        if not w:
            w = self.owner.ui.viewport.offset_w - 1
        if not h:
            h = self.owner.ui.viewport.offset_h - 1
        i = 0
        while i <= n:
            blt.layer(i)
            blt.clear_area(1, 1, w, h)
            i += 1
