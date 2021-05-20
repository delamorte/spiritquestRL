import variables
from data import json_data
from components.ai import BasicMonster
from components.fighter import Fighter


def get_fighter_data(name):

    a = json_data.data.fighters[name]
    fighter_component = Fighter(hp=a["hp"], ac=a["ac"], ev=a["ev"], power=a["power"],
                                mv_spd=a["mv_spd"], atk_spd=a["atk_spd"], size=a["size"], fov=a["fov"])
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
