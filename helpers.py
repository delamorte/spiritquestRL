def get_article(s):
    vowels = ["a","e","i","o","u"]
    def_articles = ["remains", "stairs"]
    
    if s[0].lower() in vowels:
        return "an"
    elif s.lower().split(" ", 1)[0] in def_articles:
        return "the"
    else:
        return "a"
    