def get_article(s):
    vowels = ["a","e","i","o","u"]
    if s[0].lower() in vowels:
        return "an"
    else:
        return "a"
    