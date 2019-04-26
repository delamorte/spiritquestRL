from bearlibterminal import terminal as blt
from draw import clear_camera, draw_ui
from map_objects.tilemap import init_tiles, tilemap, bestiary, abilities
from ui.elements import init_ui
import variables


def main_menu(resume=False):

    current_range = 0
    center_x = int(variables.viewport_x / 2)
    center_y = int(variables.viewport_y / 2)
    while True:

        choices = ["New game", "Resize window",
                   "Graphics: " + variables.gfx, "Tilesize: " + variables.tilesize + "x" + variables.tilesize, "Exit"]
        if resume:
            choices.insert(0, "Resume game")
        blt.layer(0)
        clear_camera()
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
            if variables.gfx is "tiles":
                variables.gfx = "ascii"
            elif variables.gfx is "ascii":
                variables.gfx = "tiles"

        if key == blt.TK_ENTER and r == "Tilesize: " + variables.tilesize + "x" + variables.tilesize:
            if int(variables.tilesize) < 48:
                variables.tilesize = str(int(variables.tilesize) + 16)
                # blt.close()
                init_tiles()
                msg_panel, msg_panel_borders, screen_borders = init_ui()
                draw_ui(msg_panel, msg_panel_borders, screen_borders)
            else:
                variables.tilesize = str(16)
                # blt.close()
                init_tiles()
                msg_panel, msg_panel_borders, screen_borders = init_ui()
                draw_ui(msg_panel, msg_panel_borders, screen_borders)

        if key == blt.TK_ENTER and r is "New game":
            key = None
            while True:
                clear_camera()
                animals = tilemap()["monsters"]
                exclude = {"frog"}
                animals = {x: animals[x] for x in animals if x not in exclude}
                blt.layer(0)
                blt.puts(center_x, center_y - 5,
                         "[color=white]Choose your spirit animal...", 0, 0, blt.TK_ALIGN_CENTER)
                for i, (r, c) in enumerate(animals.items()):
                    selected = i == current_range

                    # Draw select symbol, monster name and description
                    blt.color("orange" if selected else "default")
                    blt.puts(center_x - 14, center_y - 2 + i * 5, "%s%s" %
                             ("[U+203A]" if selected else " ", r.capitalize() + ":" + "\n " + bestiary()[r]), 0, 0, blt.TK_ALIGN_LEFT)
                    
                    if r == "crow":
                        blt.puts(center_x - 14+1, center_y - 2 + i * 5 +2, "reveal: " + abilities()["reveal"], 0, 0, blt.TK_ALIGN_LEFT)
                        blt.puts(center_x - 14+1, center_y - 2 + i * 5 +3, "swoop: " + abilities()["swoop"], 0, 0, blt.TK_ALIGN_LEFT)
                    
                    if r == "rat":
                        blt.puts(center_x - 14+1, center_y - 2 + i * 5 +2, "paralyzing bite: " + abilities()["paralyzing bite"], 0, 0, blt.TK_ALIGN_LEFT)
                        blt.puts(center_x - 14+1, center_y - 2 + i * 5 +3, "stealth", 0, 0, blt.TK_ALIGN_LEFT)
                        
                    if r == "snake":
                        blt.puts(center_x - 14+1, center_y - 2 + i * 5 +2, "poison bite: " + abilities()["poison bite"], 0, 0, blt.TK_ALIGN_LEFT)

                    # Draw a bg tile
                    blt.layer(0)
                    blt.puts(center_x - 20 + 1, center_y - 2 + i *
                             5, "[U+" + hex(0xE900 + 3) + "]", 0, 0)

                    # Draw monster tile
                    blt.layer(1)
                    if variables.gfx is "ascii":
                        blt.puts(center_x - 20 + 1,
                                 center_y - 2 + i * 5, c, 0, 0)
                    else:
                        blt.puts(center_x - 20 + 1, center_y - 2 +
                                 i * 5, "[U+" + hex(c + 2048) + "]", 0, 0)

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

        elif key == blt.TK_ENTER and r is "Resize window":
            blt.set("window: resizeable=true, minimum-size=60x20")
            key = None
            while key not in (blt.TK_CLOSE, blt.TK_ESCAPE, blt.TK_ENTER):
                msg_panel, msg_panel_borders, screen_borders = init_ui()
                center_x = int(variables.viewport_x / 2)
                center_y = int(variables.viewport_y / 2)
                h = blt.state(blt.TK_HEIGHT)
                w = blt.state(blt.TK_WIDTH)
                draw_ui(msg_panel, msg_panel_borders, screen_borders)
                clear_camera(variables.viewport_x, variables.viewport_y)
                blt.puts(center_x + 2, center_y,
                         "[color=white]Use arrow keys or drag window borders to resize.\n Alt+Enter for fullscreen.\n Press Enter or Esc when done.", 0, 0, blt.TK_ALIGN_CENTER)
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

            blt.set("window: resizeable=false")
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
    center_x = int(variables.viewport_x / 2)
    center_y = int(variables.viewport_y / 2)

    while True:
        clear_camera()
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
            blt.puts(center_x - 14, center_y - 2 + i * 3, "%s%s" %
                     ("[U+203A]" if selected else " ", r.capitalize() + ":" + "\n " + bestiary()[r]), 0, 0, blt.TK_ALIGN_LEFT)

            # Draw a bg tile
            blt.layer(0)
            blt.puts(center_x - 20 + 1, center_y - 2 + i *
                     3, "[U+" + hex(0xE900 + 3) + "]", 0, 0)

            # Draw monster tile
            blt.layer(1)
            if variables.gfx is "ascii":
                blt.puts(center_x - 20 + 1, center_y - 2 + i * 3, c, 0, 0)
            else:
                blt.puts(center_x - 20 + 1, center_y - 2 + i *
                         3, "[U+" + hex(c + 2048) + "]", 0, 0)

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
            if current_range < len(avatars) - 1:
                current_range += 1
        elif key == blt.TK_ENTER:
            player.fighter = player.player.avatar[choice]
            player.char = player.player.char[choice]
            return choice
