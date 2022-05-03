from bearlibterminal import terminal as blt


def handle_keys(key):

    # Movement keys
    if key == blt.TK_LEFT or key == blt.TK_KP_4  or key == blt.TK_H:
        return {'move': (-1, 0)}
    elif key == blt.TK_DOWN or key == blt.TK_KP_2  or key == blt.TK_J:
        return {'move': (0, 1)}
    elif key == blt.TK_UP or key == blt.TK_KP_8 or key == blt.TK_K:
        return {'move': (0, -1)}
    elif key == blt.TK_RIGHT or key == blt.TK_KP_6  or key == blt.TK_L:
        return {'move': (1, 0)}
    elif key == blt.TK_KP_7 or key == blt.TK_Y:
        return {'move': (-1, -1)}
    elif key == blt.TK_KP_1 or key == blt.TK_B:
        return {'move': (-1, 1)}
    elif key == blt.TK_KP_9 or key == blt.TK_U:
        return {'move': (1, -1)}
    elif key == blt.TK_KP_3 or key == blt.TK_N:
        return {'move': (1, 1)}

    if key == blt.TK_G or key == blt.TK_COMMA:
        return {'pickup': True}

    if key == blt.TK_C or key == blt.TK_ENTER:
        return {'interact': True}

    # '<' and '> keys for stairs
    if key == 49:
        return {'stairs': True}

    # Toggle full screen
    if key == blt.TK_FULLSCREEN:
        return {'fullscreen': True}

    # Close window
    if key == blt.TK_CLOSE:
        return {'close': True}

    if key == blt.TK_ESCAPE:
        return {'main_menu': True}

    if key == blt.TK_F1:
        return {'avatar_info': True}

    if key == blt.TK_F2:
        return {'level_up': True}

    if key == blt.TK_I:
        return {'inventory': True}

    if key == blt.TK_M:
        return {'msg_history': True}

    if key == blt.TK_PERIOD or key == blt.TK_KP_5:
        return {'wait': True}

    if key == blt.TK_X:
        return {'examine': True}

    if key in [blt.TK_1, blt.TK_2, blt.TK_3, blt.TK_4, blt.TK_5, blt.TK_6, blt.TK_7, blt.TK_8, blt.TK_9, blt.TK_0,
               blt.TK_W, blt.TK_A]:
        return {'switch_ability': True}

    if key == blt.TK_Z or key == blt.TK_TAB or key == blt.TK_ENTER:
        return {'use_ability': True}

    # No key was pressed
    return {}
