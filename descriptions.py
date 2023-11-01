def bestiary():

    animals = {"crow": "quick, very agile, very weak, excellent vision",
               "rat": "very quick, agile, weak, small, poor vision",
               "snake": "strong, slow, small, average vision",
               "frog": "no description",
               "bear": "no description",
               "felid": "no description",
               "mosquito": "no description",
               "chaos cat": "no description",
               "chaos bear": "no description",
               "cockroach": "no description",
               "bone snake": "no description",
               "chaos dog": "no description",
               "bat": "no description",
               "imp": "no description",
               "leech": "no description",
               "spirit": "no description",
               "chaos spirit": "no description",
               "ghost dog": "no description",
               "gecko": "no description",
               "serpent": "no description",
               "fairy": "no description",
               "king kobra": "no description",
               "albino rat": "no description",
               "keeper of dreams": "no description"
    }
    return animals


def abilities():
    # Abilities are organized in separate categories.
    # attack: ability name: [description, dmg, effect]
    abilities = {"attack":
                 {"poison bite": ["1d6, may poison", "1d6", "poison"],
                     "paralyzing bite": ["1d4, may paralyze", "1d5", "paralyze"],
                     "swoop": ["2d3, extra dmg on small targets", "2d3", ""],
                     "claw": ["1d6", "1d6", ""]},

                 "move":
                 {"leap": "leap to a tile in a radius 4"},

                 "utility":
                 {"reveal": "reveal an area of radius 8 around you, may reveal secrets."}}
    return abilities
