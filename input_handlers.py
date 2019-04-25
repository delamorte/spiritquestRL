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

    # '<' and '> keys for stairs
    if key == 41 or key == 49:
        return {'stairs': True}

    # Toggle full screen
    if key == blt.TK_FULLSCREEN:
        return {'fullscreen': True}

    # No key was pressed
    return {}
