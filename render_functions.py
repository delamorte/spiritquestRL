from bearlibterminal import terminal as blt
from collections import Counter
from helpers import get_article
from math import ceil
from textwrap import shorten, fill
import numpy as np
from map_objects.tilemap import tilemap, tilemap_ui
from scipy.spatial.distance import cityblock
import settings
from palettes import argb_from_color
import random
from ctypes import c_uint32, addressof


class RenderFunctions:
    def __init__(self, ui_offset_x=0, ui_offset_y=0):
        self.light_sources = None
        self.owner = None
        self.ui_offset_x = ui_offset_x
        self.ui_offset_y = ui_offset_y

    def draw(self, entity, x, y):
        player = self.owner.player
        game_map = self.owner.levels.current_map
        # Draw the entity to the screen
        blt.layer(entity.layer)
        blt.color(entity.color)
        c = blt.color_from_name(entity.color)
        if not entity.cursor:
            light_map = player.player.lightmap
            argb = argb_from_color(c)
            a = argb[0]
            r = min(int(argb[1] * light_map[entity.y][entity.x]), 255)
            g = min(int(argb[2] * light_map[entity.y][entity.x]), 255)
            b = min(int(argb[3] * light_map[entity.y][entity.x]), 255)

            blt.color(blt.color_from_argb(a, r, g, b))

        if not (player.light_source.fov_map.fov[entity.y, entity.x] and
                game_map.tiles[entity.x][entity.y].explored):
            blt.color("dark gray")

        # Cursor needs some offset in ascii
        if settings.gfx == "ascii" and entity.name == "cursor":
            blt.put_ext(x * settings.tile_offset_x, y *
                        settings.tile_offset_y, -3 * settings.tile_offset_x, -5 * settings.tile_offset_y, entity.char)
        else:
            if entity.boss and not entity.fighter:
                blt.put((x - 1) * settings.tile_offset_x, (y - 1) *
                        settings.tile_offset_y, entity.char)
            else:
                blt.put(x * settings.tile_offset_x, y *
                        settings.tile_offset_y, entity.char)

    def draw_entities(self, entities):
        game_camera = self.owner.game_camera
        player = self.owner.player
        game_map = self.owner.levels.current_map
        cursor = self.owner.cursor
        stack = self.owner.message_log.stack
        self.light_sources = []
        for entity in entities:

            x, y = game_camera.get_coordinates(entity.x, entity.y)

            if entity.x == player.x and entity.y == player.y and entity.stand_on_messages:

                stack.append(get_article(
                    entity.name).capitalize() + " " + entity.name)
                if entity.xtra_info:
                    stack.append(entity.xtra_info)

            if cursor:
                if entity.occupied_tiles is not None:
                    if (game_map.tiles[entity.x][entity.y].explored and not entity.cursor and
                            (cursor.x, cursor.y) in entity.occupied_tiles):

                        stack.append(get_article(entity.name).capitalize() + " " + entity.name)
                        stack.append(str("x: " + (str(cursor.x) + ", y: " + str(cursor.y))))

                        if entity.xtra_info:
                            stack.append(entity.xtra_info)

                        if entity.fighter:
                            self.draw_stats(entity)

                elif (entity.x == cursor.x and entity.y == cursor.y and not
                entity.cursor and game_map.tiles[entity.x][entity.y].explored):

                    stack.append(get_article(entity.name).capitalize() + " " + entity.name)
                    stack.append(str("x: " + (str(cursor.x) + ", y: " + str(cursor.y))))

                    if entity.xtra_info:
                        stack.append(entity.xtra_info)

                    if entity.fighter:
                        self.draw_stats(entity)

                if entity.name == "cursor":
                    self.clear(entity, entity.last_seen_x, entity.last_seen_y)
                    self.draw(entity, x, y)

            if not entity.cursor and player.light_source.fov_map.fov[entity.y, entity.x]:
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

            elif (not player.light_source.fov_map.fov[entity.y, entity.x] and
                  game_map.tiles[entity.last_seen_x][entity.last_seen_y].explored and not
                  player.light_source.fov_map.fov[entity.last_seen_y, entity.last_seen_x]):

                x, y = game_camera.get_coordinates(entity.last_seen_x, entity.last_seen_y)

                if entity.light_source and not entity.fighter:
                    self.light_sources.append(entity.light_source)
                else:
                    self.draw(entity, x, y)

            if player.light_source.fov_map.fov[entity.y, entity.x] and entity.ai and settings.gfx != "ascii":
                self.draw_indicator(player.x, player.y, "gray")
                self.draw_indicator(entity.x, entity.y, "dark red", entity.occupied_tiles)

    def draw_map(self):
        game_camera = self.owner.game_camera
        game_map = self.owner.levels.current_map
        player = self.owner.player
        # Set boundaries where to draw map
        bound_x = game_camera.bound_x
        bound_y = game_camera.bound_y
        bound_x2 = game_camera.bound_x2
        bound_y2 = game_camera.bound_y2
        # Clear what's drawn in camera
        self.clear_camera(5)
        # Set boundaries if map is smaller than viewport
        if game_map.width < game_camera.width:
            bound_x2 = game_map.width
        if game_map.height < game_camera.height:
            bound_y2 = game_map.height
        # Draw all the tiles within the boundaries of the game camera
        center = np.array([player.y, player.x])
        entities = []
        for y in range(bound_y, bound_y2):
            for x in range(bound_x, bound_x2):
                map_x, map_y = game_camera.x + x, game_camera.y + y
                if game_map.width < game_camera.width:
                    map_x = x
                if game_map.height < game_camera.height:
                    map_y = y
                visible = player.light_source.fov_map.fov[map_y, map_x]

                # Draw tiles within fov
                if visible:
                    blt.layer(0)
                    dist = float(cityblock(center, np.array([map_y, map_x])))
                    light_level = game_map.tiles[map_x][map_y].natural_light_level * \
                                  (1.0 / (1.05 + 0.035 * dist + 0.025 * dist * dist))
                    player.player.lightmap[map_y][map_x] = light_level

                    c = blt.color_from_name(game_map.tiles[map_x][map_y].color)

                    argb = argb_from_color(c)
                    a = argb[0]
                    r = min(int(argb[1] * light_level), 255)
                    g = min(int(argb[2] * light_level), 255)
                    b = min(int(argb[3] * light_level), 255)
                    blt.color(blt.color_from_argb(a, r, g, b))

                    blt.put(x * settings.tile_offset_x, y * settings.tile_offset_y,
                            game_map.tiles[map_x][map_y].char)

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
                            blt.put(x * settings.tile_offset_x, y * settings.tile_offset_y,
                                    tile[0])
                            i += 1

                    # Set everything in fov as explored
                    game_map.tiles[map_x][map_y].explored = True

                # Gray out explored tiles
                elif game_map.tiles[map_x][map_y].explored:
                    blt.layer(0)
                    blt.color("darkest gray")
                    blt.put(x * settings.tile_offset_x, y * settings.tile_offset_y,
                            game_map.tiles[map_x][map_y].char)
                    if len(game_map.tiles[map_x][map_y].layers) > 0:
                        i = 1
                        for tile in game_map.tiles[map_x][map_y].layers:
                            blt.layer(i)
                            blt.put(x * settings.tile_offset_x, y * settings.tile_offset_y,
                                    tile[0])
                            i += 1

                if len(game_map.tiles[map_x][map_y].entities_on_tile) > 0:
                    for n in game_map.tiles[map_x][map_y].entities_on_tile:
                        if n not in entities:
                            entities.append(n)

        self.draw_entities(entities)
        if len(self.light_sources) > 0:
            self.draw_light_sources()

    def draw_light_sources(self):
        player = self.owner.player
        light_map = player.player.lightmap
        game_map = self.owner.levels.current_map
        game_camera = self.owner.game_camera
        for light in self.light_sources:
            light_fov = np.where(light.fov_map.fov)
            center = np.array([light.owner.y, light.owner.x])

            for i in range(light_fov[0].size):
                y, x = int(light_fov[0][i]), int(light_fov[1][i])
                if player.light_source.fov_map.fov[y, x]:
                    v = np.array([y, x])
                    dist = float(cityblock(center, v))
                    light_level = game_map.tiles[x][y].natural_light_level * \
                                  (1.0 / (0.2 + 0.1 * dist + 0.025 * dist * dist))

                    if light_map[y][x] < light_level:
                        light_map[y][x] = light_level

        player_fov = np.where(player.light_source.fov_map.fov)
        for j in range(player_fov[0].size):
            y, x = int(player_fov[0][j]), int(player_fov[1][j])
            cam_x, cam_y = game_camera.get_coordinates(x, y)
            blt.layer(0)
            c = blt.color_from_name(game_map.tiles[x][y].color)
            argb = argb_from_color(c)
            flicker = random.uniform(0.95, 1.05) if settings.flicker is True else 1
            a = argb[0]
            r = min(int(argb[1] * light_map[y][x] * flicker), 255)
            g = min(int(argb[2] * light_map[y][x] * flicker), 255)
            b = min(int(argb[3] * light_map[y][x] * flicker), 255)

            blt.color(blt.color_from_argb(a, r, g, b))
            blt.put(cam_x * settings.tile_offset_x, cam_y * settings.tile_offset_y,
                    game_map.tiles[x][y].char)

            if len(game_map.tiles[x][y].layers) > 0:
                i = 1
                for tile in game_map.tiles[x][y].layers:
                    blt.layer(i)
                    c = blt.color_from_name(tile[1])
                    argb = argb_from_color(c)
                    a = argb[0]
                    r = min(int(argb[1] * light_map[y][x] * flicker), 255)
                    g = min(int(argb[2] * light_map[y][x] * flicker), 255)
                    b = min(int(argb[3] * light_map[y][x] * flicker), 255)
                    blt.color(blt.color_from_argb(a, r, g, b))
                    blt.put(cam_x * settings.tile_offset_x, cam_y * settings.tile_offset_y,
                            tile[0])
                    i += 1

            if len(game_map.tiles[x][y].entities_on_tile) > 0:
                for entity in game_map.tiles[x][y].entities_on_tile:

                    if not entity.cursor:
                        self.clear(entity, cam_x, cam_y)
                        self.draw(entity, cam_x, cam_y)

    def draw_messages(self):
        message_log = self.owner.message_log
        stack = message_log.stack
        old_stack = message_log.old_stack
        msg_panel = self.owner.ui.msg_panel
        if len(stack) > 0 and not stack == old_stack:

            d = dict(Counter(stack))
            formatted_stack = []
            for i in d:
                if d[i] > 1:
                    formatted_stack.append(i + " x" + str(d[i]))
                else:
                    formatted_stack.append(i)
            message_log.send(
                ". ".join(formatted_stack) + ".")

        if message_log.new_msgs:
            blt.layer(0)
            blt.clear_area(msg_panel.x * self.ui_offset_x, msg_panel.y * self.ui_offset_y, msg_panel.w *
                           self.ui_offset_x, msg_panel.h * self.ui_offset_y)

            # Print the game messages, one line at a time. Display newest
            # msg at the bottom and scroll others up
            i = 4
            # if i > message_log.max_length:
            #    i = 0
            for idx, msg in enumerate(message_log.buffer):
                blt.color(message_log.buffer_colors[idx])
                msg = shorten(msg, msg_panel.w * self.ui_offset_x - 2,
                              placeholder="..(Press 'M' for log)")
                blt.puts(msg_panel.x * self.ui_offset_x + 1, msg_panel.y *
                         self.ui_offset_y - 1 + i * 2, "[offset=0,0]" + msg, msg_panel.w * self.ui_offset_x - 2,
                         1,
                         align=blt.TK_ALIGN_LEFT)
                i -= 1
            message_log.new_msgs = False

    def draw_stats(self, target=None):
        player = self.owner.player
        power_msg = "[color=light azure]Spirit power left: " + str(player.player.spirit_power)
        blt.layer(0)
        blt.clear_area(2, self.owner.ui.viewport.h + self.ui_offset_y + 3,
                       self.owner.ui.viewport.center_x + int(len(power_msg) / 2 + 5) - 5, 1)
        blt.color("gray")

        # Draw spirit power left and position it depending on window size
        if self.owner.ui.viewport.w > 90:
            blt.color("default")
            blt.puts(self.owner.ui.viewport.center_x,
                     self.owner.ui.viewport.h + self.ui_offset_y + 1, "[offset=0,-2]" + power_msg, 0, 0,
                     blt.TK_ALIGN_CENTER)
        else:
            blt.color("default")
            blt.puts(self.owner.ui.viewport.w - len(power_msg),
                     self.owner.ui.viewport.h + self.ui_offset_y + 1, "[offset=0,-2]" + power_msg, 0, 0,
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

        active_effects = []
        for x in player.status_effects.items:
            active_effects.append(x.description + "(" + str(x.duration + 1) + ")")
            if x.name == "poison":
                hp_player = "[color=green]HP:" + \
                            str(player.fighter.hp) + "/" + \
                            str(player.fighter.max_hp) + "  "

        if active_effects:
            blt.puts(4, self.owner.ui.viewport.h + self.ui_offset_y + 3,
                     "[offset=0,-2]" + "  ".join(active_effects) + "  ",
                     0, 0, blt.TK_ALIGN_LEFT)

        ac_player = "[color=default]AC:" + str(player.fighter.ac) + "  "
        ev_player = "EV:" + str(player.fighter.ev) + "  "
        power_player = "ATK:" + str(player.fighter.power) + "  "
        lvl_player = "LVL:" + str(player.player.char_level) + "  "
        exp_player = "EXP:" + str(player.player.char_exp["player"]) + "/" + \
                     str(player.player.char_level * player.player.exp_lvl_interval)

        blt.puts(4, self.owner.ui.viewport.h + self.ui_offset_y + 1,
                 "[offset=0,-2]" + "[color=lightest green]Player:  " +
                 hp_player + ac_player + ev_player + power_player + lvl_player + exp_player,
                 0, 0, blt.TK_ALIGN_LEFT)

        # Draw target stats
        if target:
            blt.clear_area(self.owner.ui.viewport.center_x - int(len(power_msg) / 2) - 5,
                           self.owner.ui.viewport.h + self.ui_offset_y + 1, self.owner.ui.viewport.w, 1)
            if target.fighter.hp / target.fighter.max_hp < 0.34:
                hp_target = "[color=light red]HP:" + \
                            str(target.fighter.hp) + "/" + \
                            str(target.fighter.max_hp) + "  "
            else:
                hp_target = "[color=default]HP:" + \
                            str(target.fighter.hp) + "/" + \
                            str(target.fighter.max_hp) + "  "
            ac_target = "[color=default]AC:" + str(target.fighter.ac) + "  "
            ev_target = "EV:" + str(target.fighter.ev) + "  "
            power_target = "ATK:" + str(target.fighter.power) + " "

            blt.puts(self.owner.ui.viewport.w, self.owner.ui.viewport.h + self.ui_offset_y + 1,
                     "[offset=0,-2]" + "[color=lightest red]" + target.name.capitalize() + ":  " + hp_target + ac_target + ev_target + power_target,
                     0, 0, blt.TK_ALIGN_RIGHT)

            if target.fighter.hp <= 0:
                blt.clear_area(2, self.owner.ui.viewport.h +
                               self.ui_offset_y + 1, self.owner.ui.viewport.w, 1)

    def draw_ui(self, element):
        blt.color(element.color)
        blt.layer(1)

        # Draw borders
        for y in range(element.offset_y, element.offset_y2):
            for x in range(element.offset_x, element.offset_x2):
                if y == element.offset_y:
                    blt.put(x, y, element.tile_horizontal)
                elif y == element.offset_y2 - 1:
                    blt.put(x, y, element.tile_horizontal)
                elif x == element.offset_x:
                    blt.put(x, y, element.tile_vertical)
                elif x == element.offset_x2 - 1:
                    blt.put(x, y, element.tile_vertical)
                if x == element.offset_x and y == element.offset_y:
                    blt.put(x, y, element.tile_nw)
                if x == element.offset_x2 - 1 and y == element.offset_y:
                    blt.put(x, y, element.tile_ne)
                if x == element.offset_x and y == element.offset_y2 - 1:
                    blt.put(x, y, element.tile_sw)
                if x == element.offset_x2 - 1 and y == element.offset_y2 - 1:
                    blt.put(x, y, element.tile_se)

    def draw_indicator(self, entity_x, entity_y, color=None, occupied_tiles=None):
        # Draw player indicator
        blt.layer(4)
        x, y = self.owner.game_camera.get_coordinates(entity_x, entity_y)
        blt.color(color)
        if occupied_tiles is not None:
            return
        else:
            blt.put(x * settings.tile_offset_x, y *
                    settings.tile_offset_y, tilemap()["indicator"])

    def draw_minimap(self):
        blt.layer(1)
        x0 = self.owner.ui.side_panel.x
        y0 = self.owner.ui.side_panel.y
        game_map = self.owner.levels.current_map

        minimap = np.ones_like(game_map.tiles, dtype=int)
        for x in range(game_map.width):
            for y in range(game_map.height):
                visible = self.owner.player.light_source.fov_map.fov[y, x]
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
                elif game_map.tiles[x][y].explored:
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

        blt.put(x0 * self.ui_offset_x + 3, y0 * self.ui_offset_y + 3, 0xF900)

    def draw_side_panel_content(self):
        game_map = self.owner.levels.current_map
        player = self.owner.player
        side_panel = self.owner.ui.side_panel
        # Draw side panel content
        blt.layer(1)
        blt.color(None)
        x_margin = 4
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
        fill_chars = 32
        for i, wpn in enumerate(weapon):
            if wpn.name == player.player.sel_weapon.name:
                # name of the selected skill
                skill_str = "Atk: {0}, {1} dmg".format(wpn.name.capitalize(), wpn.damage[wpn.rank])
                blt.puts(side_panel.offset_x + x_margin,
                         side_panel.offset_y + 30, fill(skill_str, fill_chars), 0, 0,
                         blt.TK_ALIGN_LEFT)
                # highlight icon of the selected skill
                blt.color("dark amber")
                y_margin += skill_str.count('\n')

            blt.put(side_panel.offset_x + x_margin + i * 6,
                    side_panel.offset_y + 32, wpn.icon)
            blt.color(None)

        # Attack skills
        for i, atk in enumerate(attack):
            if player.player.sel_attack and atk.name == player.player.sel_attack.name:
                skill_str = "{0}: ".format(atk.name)
                chance_str, atk_str, effect_str, duration_str = "", "", "", ""
                if atk.chance:
                    chance_str = str(int(1 / atk.chance[atk.rank])) + "% chance of "
                if atk.effect:
                    effect_str = ", ".join(atk.effect) + ", "
                if atk.duration:
                    duration_str = atk.duration[atk.rank] + " turns"
                if atk.damage:
                    atk_str = ", " + atk.damage[atk.rank] + " dmg" if duration_str else atk.damage[atk.rank] + " dmg"
                skill_str += chance_str + effect_str + duration_str + atk_str

                blt.puts(side_panel.offset_x + x_margin,
                         side_panel.offset_y + 35 + y_margin,
                         fill(skill_str.capitalize(), fill_chars), 0, 0,
                         blt.TK_ALIGN_LEFT)
                # highlight icon of the selected skill
                blt.color("dark amber")
                y_margin += skill_str.count('\n')

            blt.put(side_panel.offset_x + x_margin + i * 6,
                    side_panel.offset_y + 38 + y_margin, atk.icon)
            blt.color(None)

        # Utility skills
        for i, utl in enumerate(utility):
            if player.player.sel_utility and utl.name == player.player.sel_utility.name:
                # name of the selected skill
                skill_str = utl.name
                blt.puts(side_panel.offset_x + x_margin,
                         side_panel.offset_y + 41 + y_margin,
                         fill(skill_str.capitalize(), fill_chars),
                         0, 0, blt.TK_ALIGN_LEFT)
                y_margin += skill_str.count('\n')
                blt.puts(side_panel.offset_x + x_margin,
                         side_panel.offset_y + 46 + y_margin,
                         fill(utl.description.capitalize(), fill_chars), 46 + y_margin, 0,
                         blt.TK_ALIGN_LEFT)
                # highlight icon of the selected skill
                blt.color("dark amber")

            blt.put(side_panel.offset_x + x_margin + i * 6,
                    side_panel.offset_y + 43 + y_margin, utl.icon)
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
        blt.clear_area(x * settings.tile_offset_x, y *
                       settings.tile_offset_y, 1, 1)
        if entity.boss:
            blt.clear_area(x * settings.tile_offset_x, y *
                           settings.tile_offset_y, 2, 2)

    def clear_camera(self, n):
        w = self.owner.ui.viewport.w
        h = self.owner.ui.viewport.h
        i = 0
        while i < n:
            blt.layer(i)
            blt.clear_area(1, 1, w, h)
            i += 1
