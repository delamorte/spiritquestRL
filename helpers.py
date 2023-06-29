from random import randint


def get_article(s):
    vowels = ["a", "e", "i", "o", "u"]
    def_articles = ["remains", "stairs"]
    
    if s[0].lower() in vowels:
        return "an"
    elif s.lower().split(" ", 1)[0] in def_articles:
        return "the"
    elif s.lower() == "player":
        return ""
    else:
        return "a"


def flatten(objects):
    flat_list = []
    for i in objects:
        for item in i:
            flat_list.append(item)

    return flat_list


def roll_dice(dice_str):
    if isinstance(dice_str, int):
        return dice_str
    result = 0
    dice_arr = dice_str.split("d")
    dice_rolls = int(dice_arr[0])
    die = int(dice_arr[1])
    for x in range(dice_rolls):
        result += randint(1, die)
    return result
