from components.ai import BasicMonster
from components.fighter import Fighter


def get_fighter_stats(name):

    # Abilities are stored in tuples in a list in form
    # abilities = [(name, chance to use)]. 100 means the ability
    # is not usable by AI and has to be activated by player

    fighters = {"player": {"hp": 20, "ac": 3, "ev": 3, "power": 5, "mv_spd": 1, "atk_spd": 1, "size": "normal", "fov": 6, "abilities": []},
                "rat": {"hp": 10, "ac": 1, "ev": 4, "power": 4, "mv_spd": 2, "atk_spd": 1, "size": "small", "fov": 4, "abilities": [("paralyzing bite", 20)]},
                "crow": {"hp": 8, "ac": 1, "ev": 6, "power": 3, "mv_spd": 1.6, "atk_spd": 1, "size": "normal", "fov": 8, "abilities": [("swoop", 33), ("reveal", 100)]},
                "snake": {"hp": 12, "ac": 1, "ev": 2, "power": 5, "mv_spd": 1, "atk_spd": 1, "size": "small", "fov": 6, "abilities": [("poison bite", 20)]},
                "frog": {"hp": 15, "ac": 1, "ev": 5, "power": 5, "mv_spd": 1.4, "atk_spd": 1, "size": "small", "fov": 6, "abilities": [("leap", 20)]},
                "bear": {"hp": 20, "ac": 3, "ev": 1, "power": 6, "mv_spd": 1, "atk_spd": 1, "size": "large", "fov": 5, "abilities": [("claw", 20), ("stunning roar", 100)]},
                "felid": {"hp": 10, "ac": 2, "ev": 5, "power": 3, "mv_spd": 1.4, "atk_spd": 1, "size": "small", "fov": 6, "abilities": [("claw", 40), ("leap", 100)]},
                "mosquito": {"hp": 6, "ac": 1, "ev": 6, "power": 3, "mv_spd": 1.2, "atk_spd": 1, "size": "small", "fov": 4, "abilities": [("paralyzing bite", 10), ("poison bite", 10)]},
                "chaos cat": {"hp": 12, "ac": 3, "ev": 5, "power": 4, "mv_spd": 1.3, "atk_spd": 1, "size": "small", "fov": 6, "abilities": [("claw", 50), ("call allies", 10), ("leap", 100)]},
                "chaos bear": {"hp": 25, "ac": 4, "ev": 1, "power": 6, "mv_spd": 0.8, "atk_spd": 1, "size": "large", "fov": 5, "abilities": [("claw", 20), ("stunning roar", 100)]},
                "cockroach": {"hp": 10, "ac": 3, "ev": 3, "power": 3, "mv_spd": 0.8, "atk_spd": 1, "size": "small", "fov": 5, "abilities": [("claw", 20), ("diseasing bite", 10)]},
                "bone snake": {"hp": 15, "ac": 2, "ev": 2, "power": 5, "mv_spd": 1, "atk_spd": 1, "size": "normal", "fov": 5, "abilities": [("strangle", 20)]},
                "chaos dog": {"hp": 14, "ac": 2, "ev": 4, "power": 5, "mv_spd": 1.4, "atk_spd": 1, "size": "normal", "fov": 6, "abilities": [("claw", 40)]},
                "bat": {"hp": 10, "ac": 1, "ev": 7, "power": 3, "mv_spd": 1.4, "atk_spd": 1, "size": "small", "fov": 4, "abilities": [("leeching bite", 20)]},
                "imp": {"hp": 12, "ac": 2, "ev": 4, "power": 4, "mv_spd": 1.2, "atk_spd": 1, "size": "normal", "fov": 6, "abilities": [("claw", 20), ("call allies", 20)]},
                "leech": {"hp": 13, "ac": 3, "ev": 3, "power": 4, "mv_spd": 0.5, "atk_spd": 1, "size": "normal", "fov": 6, "abilities": [("leeching bite", 30)]},
                "spirit": {"hp": 10, "ac": 1, "ev": 6, "power": 3, "mv_spd": 1, "atk_spd": 1, "size": "normal", "fov": 6, "abilities": [("give power", 5), ("heal", 5), ("call allies", 20)]},
                "chaos spirit": {"hp": 10, "ac": 1, "ev": 6, "power": 3, "mv_spd": 1, "atk_spd": 1, "size": "normal", "fov": 6, "abilities": [("drain power", 5), ("harm", 5)]},
                "ghost dog": {"hp": 12, "ac": 2, "ev": 4, "power": 5, "mv_spd": 1.5, "atk_spd": 1, "size": "normal", "fov": 6, "abilities": [("claw", 30), ("invisibility", 5)]},
                "gecko": {"hp": 16, "ac": 3, "ev": 4, "power": 5, "mv_spd": 1, "atk_spd": 1, "size": "normal", "fov": 6, "abilities": [("fire breath", 5), ("claw", 20)]},
                "serpent": {"hp": 15, "ac": 2, "ev": 5, "power": 5, "mv_spd": 1.3, "atk_spd": 1, "size": "normal", "fov": 6, "abilities": [("strangle", 20)]},
                "fairy": {"hp": 12, "ac": 1, "ev": 4, "power": 4, "mv_spd": 1.4, "atk_spd": 1, "size": "normal", "fov": 6, "abilities": [("invisibility", 5), ("heal", 10), ("give power", 5), ("harm", 5)]},
                "king kobra": {"hp": 30, "ac": 3, "ev": 3, "power": 6, "mv_spd": 1, "atk_spd": 1, "size": "normal", "fov": 6, "abilities": [("poison bite", 20), ("strangle", 20)]},
                "albino rat": {"hp": 20, "ac": 2, "ev": 6, "power": 5, "mv_spd": 2, "atk_spd": 1, "size": "small", "fov": 6, "abilities": [("claw", 20), ("diseasing bite", 10), ("poison bite", 0), ("call allies", 20)]},
                "keeper of dreams": {"hp": 50, "ac": 3, "ev": 6, "power": 5, "mv_spd": 0.7, "atk_spd": 1, "size": "gigantic", "fov": 6, "abilities": [("claw", 20), ("diseasing bite", 10), ("poison bite", 20), ("call allies", 20)]},}

    a = fighters[name]
    fighter_component = Fighter(hp=a["hp"], ac=a["ac"], ev=a["ev"], power=a["power"], mv_spd=a["mv_spd"],
                                atk_spd=a["atk_spd"], size=a["size"], fov=a["fov"], abilities=a["abilities"])

    return fighter_component


def get_fighter_ai(name):

    ai_component = BasicMonster()

    return ai_component


def get_spawn_rates(monsters):

    rates = {"rat": 0.2,
             "crow": 0.2,
             "snake": 0.2,
             "frog": 0.15,
             "bear": 0.10,
             "felid": 0.20,
             "mosquito": 0.10,
             "chaos cat": 0.05,
             "chaos bear": 0.03,
             "cockroach": 0.20,
             "bone snake": 0.10,
             "chaos dog": 0.15,
             "bat": 0.2,
             "imp": 0.15,
             "leech": 0.15,
             "spirit": 0.15,
             "chaos spirit": 0.10,
             "ghost dog": 0.15,
             "gecko": 0.10,
             "serpent": 0.05,
             "fairy": 0.07}

    spawn_rates = []
    for mon in monsters:
        spawn_rates.append(rates[mon[0]])
    
    return spawn_rates
