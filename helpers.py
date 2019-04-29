def get_article(s):
    vowels = ["a","e","i","o","u"]
    if s[0].lower() in vowels:
        return "an"
    elif s.lower().split(" ", 1)[0] == "remains":
        return "the"
    else:
        return "a"
    