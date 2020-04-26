from bearlibterminal import terminal as blt
from descriptions import abilities, bestiary, meditate_params
from draw import clear_camera, draw_ui
from map_objects.tilemap import init_tiles, tilemap
import variables
from random import sample
from palettes import get_monster_color
from os import path
from textwrap import wrap


def main_menu(resume=False, ui_elements=None):
    current_range = 0
    center_x = int(variables.viewport_w / 2)
    center_y = int(variables.viewport_h / 2)

    while True:

        choices = ["New game", "Resize window",
                   "Graphics: " + variables.gfx, "Tilesize: " + variables.tile_width + "x" + variables.tile_height,
                   "Exit"]
        if resume:
            choices = ["New game", "Resize window",
                       "Graphics: " + variables.gfx + " (restart game to change)",
                       "Tilesize: " + variables.tile_width + "x" + variables.tile_height + " (restart game to change)",
                       "Exit"]
            choices.insert(0, "Resume game")

        blt.layer(0)
        clear_camera(5)
        blt.puts(center_x + 2, center_y,
                 "[color=white]Spirit Quest RL", 0, 0, blt.TK_ALIGN_CENTER)

        for i, r in enumerate(choices):
            selected = i == current_range
            blt.color("orange" if selected else "light_gray")
            blt.puts(center_x + 2, center_y + 2 + i, "%s%s" %
                     ("[U+203A]" if selected else " ", r), 0, 0, blt.TK_ALIGN_CENTER)

        blt.refresh()

        r = choices[current_range]

        key = blt.read()
        if key in (blt.TK_ESCAPE, blt.TK_CLOSE):
            exit()

        if key == blt.TK_ENTER and not resume and r == "Graphics: " + variables.gfx:
            if variables.gfx == "adambolt":
                variables.gfx = "ascii"
                variables.tile_height = str(24)
                variables.tile_width = str(16)
                init_tiles()
                ui_elements.init_ui()
                draw_ui(ui_elements)
            elif variables.gfx == "ascii":
                variables.gfx = "oryx"
                variables.tile_height = str(48)
                variables.tile_width = str(32)
                init_tiles()
                ui_elements.init_ui()
                draw_ui(ui_elements)
            elif variables.gfx == "oryx":
                variables.gfx = "adambolt"
                variables.tile_height = str(48)
                variables.tile_width = str(32)
                init_tiles()
                ui_elements.init_ui()
                draw_ui(ui_elements)

        if key == blt.TK_ENTER and not resume and r == "Tilesize: " + \
                variables.tile_width + "x" + variables.tile_height:
            if int(variables.tile_height) == 48:
                variables.tile_height = str(24)
                variables.tile_width = str(16)
                init_tiles()
                ui_elements.init_ui()
                draw_ui(ui_elements)
            else:
                variables.tile_height = str(48)
                variables.tile_width = str(32)
                init_tiles()
                ui_elements.init_ui()
                draw_ui(ui_elements)

        if key == blt.TK_ENTER and r is "New game":

            current_range = 0
            while True:
                clear_camera(5)
                animals = tilemap()["monsters"]
                # exclude = {"frog"}
                animals = {x: animals[x] for x in ("crow", "rat", "snake")}
                blt.layer(0)
                blt.puts(center_x, center_y - 5,
                         "[color=white]Choose your spirit animal...", 0, 0, blt.TK_ALIGN_CENTER)
                for i, (r, c) in enumerate(animals.items()):
                    selected = i == current_range

                    # Draw select symbol, monster name and description
                    blt.color("orange" if selected else "default")
                    blt.puts(center_x - 24, center_y - 2 + i * 5 + 1, "%s%s" %
                             ("[U+203A]" if selected else " ", r.capitalize() + ":" + "\n " + bestiary()[r]), 0, 0,
                             blt.TK_ALIGN_LEFT)

                    if r == "crow":
                        blt.puts(center_x - 24 + 1, center_y - 2 + i * 5 + 2,
                                 "reveal: " + abilities()["utility"]["reveal"], 50, 0, blt.TK_ALIGN_LEFT)
                        blt.puts(center_x - 24 + 1, center_y - 2 + i * 5 + 4,
                                 "swoop: " + abilities()["attack"]["swoop"][0], 0, 0, blt.TK_ALIGN_LEFT)

                    if r == "rat":
                        blt.puts(center_x - 24 + 1, center_y - 2 + i * 5 + 2,
                                 "paralyzing bite: " + abilities()["attack"]["paralyzing bite"][0], 0, 0,
                                 blt.TK_ALIGN_LEFT)
                        blt.puts(center_x - 24 + 1, center_y - 2 + i * 5 + 3, "stealth", 0, 0, blt.TK_ALIGN_LEFT)

                    if r == "snake":
                        blt.puts(center_x - 24 + 1, center_y - 2 + i * 5 + 2,
                                 "poison bite: " + abilities()["attack"]["poison bite"][0], 0, 0, blt.TK_ALIGN_LEFT)

                    if variables.gfx == "adambolt":
                        # Draw a bg tile
                        blt.layer(0)
                        blt.puts(center_x - 30 + 1, center_y - 2 + i *
                                 5, "[U+" + hex(0xE800 + 3) + "]", 0, 0)

                    # Draw monster tile
                    blt.layer(1)
                    blt.color(get_monster_color(r))
                    if variables.gfx == "adambolt":
                        blt.color(None)
                    if variables.gfx == "ascii":
                        blt.puts(center_x - 30 + 1,
                                 center_y - 2 + i * 5, c, 0, 0)
                    else:
                        blt.puts(center_x - 30 + 1, center_y - 2 +
                                 i * 5, "[U+" + hex(c) + "]", 0, 0)

                    if selected:
                        choice = r

                blt.refresh()
                key = blt.read()

                if key == blt.TK_ESCAPE:
                    break
                elif key == blt.TK_UP:
                    if current_range > 0:
                        current_range -= 1
                elif key == blt.TK_DOWN:
                    if current_range < len(animals) - 1:
                        current_range += 1
                elif key == blt.TK_ENTER:
                    return choice

        elif key == blt.TK_ENTER and r is "Exit":
            exit()

        elif key == blt.TK_ENTER and not resume and r is "Resize window":
            blt.set("window: resizeable=true, minimum-size=60x20")
            key = None
            while key not in (blt.TK_CLOSE, blt.TK_ESCAPE, blt.TK_ENTER):
                ui_elements.init_ui()
                center_x = int(variables.viewport_w / 2)
                center_y = int(variables.viewport_h / 2)
                h = blt.state(blt.TK_HEIGHT)
                w = blt.state(blt.TK_WIDTH)
                draw_ui(ui_elements)
                clear_camera(5)
                blt.puts(center_x + 2, center_y,
                         "[color=white]Use arrow keys or drag window borders to resize.\n Alt+Enter for fullscreen.\n Press Enter or Esc when done.",
                         0, 0, blt.TK_ALIGN_CENTER)
                blt.refresh()

                key = blt.read()
                if key == blt.TK_FULLSCREEN:
                    blt.set("window.fullscreen=true")
                if key == blt.TK_UP:
                    blt.set("window: size=" + str(w) + "x" +
                            (str(h + variables.tile_offset_y)))
                if key == blt.TK_DOWN:
                    blt.set("window: size=" + str(w) + "x" +
                            (str(h - variables.tile_offset_y)))
                    if h <= 30:
                        blt.set("window: size=" + str(w) + "x" + "30")
                if key == blt.TK_RIGHT:
                    blt.set("window: size=" +
                            (str(w + variables.tile_offset_x)) + "x" + str(h))
                if key == blt.TK_LEFT:
                    blt.set("window: size=" +
                            (str(w - variables.tile_offset_x)) + "x" + str(h))
                    if w <= 60:
                        blt.set("window: size=60" + "x" + str(h))

            clear_camera(5)
            blt.refresh()
        elif key == blt.TK_UP:
            if current_range > 0:
                current_range -= 1
        elif key == blt.TK_DOWN:
            if current_range < len(choices) - 1:
                current_range += 1

        elif key == blt.TK_ENTER and r == "Resume game":
            break


def choose_avatar(player):
    key = None
    current_range = 0
    center_x = int(variables.viewport_w / 2)
    center_y = int(variables.viewport_h / 2)

    while True:
        clear_camera(5)
        animals = player.player.char
        exclude = {"player"}
        avatars = {x: animals[x] for x in animals if x not in exclude}
        blt.layer(0)
        blt.puts(center_x, center_y - 5,
                 "[color=white]Choose your spirit animal...", 0, 0, blt.TK_ALIGN_CENTER)
        for i, (r, c) in enumerate(avatars.items()):
            selected = i == current_range

            # Draw select symbol, monster name and description
            blt.color("orange" if selected else "default")
            blt.puts(center_x - 24, center_y - 2 + i * 3, "%s%s" %
                     ("[U+203A]" if selected else " ", r.capitalize() + ":" + "\n " + bestiary()[r]), 0, 0,
                     blt.TK_ALIGN_LEFT)

            if variables.gfx == "adambolt":
                # Draw a bg tile
                blt.layer(0)
                blt.puts(center_x - 30 + 1, center_y - 2 + i *
                         5, "[U+" + hex(0xE800 + 3) + "]", 0, 0)

            # Draw monster tile
            blt.layer(1)
            blt.color(get_monster_color(r))
            if variables.gfx == "adambolt":
                blt.color(None)
            if variables.gfx == "ascii":
                blt.puts(center_x - 30 + 1, center_y - 2 + i * 3, c, 0, 0)
            else:
                blt.puts(center_x - 30 + 1, center_y - 2 + i *
                         3, "[U+" + hex(c) + "]", 0, 0)

            if selected:
                choice = r

        blt.refresh()
        key = blt.read()

        if key == blt.TK_ESCAPE:
            return None, None
        elif key == blt.TK_UP:
            if current_range > 0:
                current_range -= 1
        elif key == blt.TK_DOWN:
            if current_range < len(avatars) - 1:
                current_range += 1
        elif key == blt.TK_ENTER:
            player.fighter = player.player.avatar[choice]
            player.char = player.player.char[choice]
            player.color = get_monster_color(choice)
            choice_params = {}
            for i in range(3):
                choice_param = set_up_level_params(i, choice_params)
                choice_params.update(choice_param)

            return choice, choice_params


def set_up_level_params(question_number, prev_choices):
    key = None
    current_range = 0
    center_x = int(variables.viewport_w / 2)
    center_y = int(variables.viewport_h / 2)
    choice_params = dict(sample(meditate_params().items(), 3))
    choice_params = {x: choice_params[x] for x in choice_params if x not in prev_choices}

    while True:
        clear_camera(2)
        blt.layer(0)
        if question_number == 0:
            blt.puts(center_x, center_y - 5,
                     "[color=white]You sit by the campfire to meditate. The world begins to drift away... ", 0, 0,
                     blt.TK_ALIGN_CENTER)
            blt.puts(center_x, center_y - 4,
                     "[color=white]Your mind gets visions of..", 0, 0, blt.TK_ALIGN_CENTER)
        if question_number == 1:
            blt.puts(center_x, center_y - 5,
                     "[color=white]Pictures of " + list(prev_choices)[0] + " begin to form in your mind.", 0, 0,
                     blt.TK_ALIGN_CENTER)
            blt.puts(center_x, center_y - 4,
                     "[color=white]Then, a new image appears..", 0, 0, blt.TK_ALIGN_CENTER)

        if question_number == 2:
            blt.puts(center_x, center_y - 5,
                     "[color=white]You have dreamt about " + list(prev_choices)[0] + ", which shall bring about " +
                     list(prev_choices)[1] + ".", 0, 0, blt.TK_ALIGN_CENTER)
            blt.puts(center_x, center_y - 4,
                     "[color=white]The last thing that enters your mind is...", 0, 0, blt.TK_ALIGN_CENTER)

        for i, r in enumerate(choice_params):
            selected = i == current_range
            blt.color("orange" if selected else "light_gray")
            blt.puts(center_x + 2, center_y + 2 + i, "%s%s" %
                     ("[U+203A]" if selected else " ", ".." + r + "."), 0, 0, blt.TK_ALIGN_CENTER)

            if selected:
                choice = {r: choice_params[r]}

        blt.refresh()
        key = blt.read()

        if key == blt.TK_ESCAPE:
            break
        elif key == blt.TK_UP:
            if current_range > 0:
                current_range -= 1
        elif key == blt.TK_DOWN:
            if current_range < len(choice_params) - 1:
                current_range += 1
        elif key == blt.TK_ENTER:
            return choice
