from bearlibterminal import terminal as blt


def handle_keys(key):

    # Movement keys
    if key == blt.TK_LEFT:
        return {'move': (-1, 0)}
    elif key == blt.TK_DOWN:
        return {'move': (0, 1)}
    elif key == blt.TK_UP:
        return {'move': (0, -1)}
    elif key == blt.TK_RIGHT:
        return {'move': (1, 0)}
    elif key == blt.TK_KP_7:
        return {'move': (-1, -1)}
    elif key == blt.TK_KP_1:
        return {'move': (-1, 1)}
    elif key == blt.TK_KP_9:
        return {'move': (1, -1)}
    elif key == blt.TK_KP_3:
        return {'move': (1, 1)}

    # Toggle full screen
    if key == blt.TK_FULLSCREEN:
        return {'fullscreen': True}

    # Exit the game
    elif key == blt.TK_CLOSE:
        return {'exit': True}

    # No key was pressed
    return {}
