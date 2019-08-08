def bestiary():

    animals = {"crow": "quick, very agile, very weak, excellent vision",
               "rat": "very quick, agile, weak, small, poor vision",
               "snake": "strong, slow, small, average vision"}
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


def meditate_params():
    # negative integers represents chaos. positive ints harmony,
    # zero is neutrality. The map will created based on these biases.
    params = {"death and decay": -3,
              "a red sun rising in the sky": -1,
              "pain, suffering and misery": -1,
              "winds of ice that soon will spread": 0,
              "a hole in the sky": 2,
              "the Mother Moon": 2,
              "a love that never dies": 3,
              "summer skies of love": 1,
              "happiness, providence of sorrow": 0,
              "deadly petals with strange power": -1,
              "a chill that numbs from head to toe": 0,
              "the day of judgement": 0,
              "a sapphire haze in the orbit": 1,
              "plastic flowers and melting sun": -1,
              "a golden chorus singing": 3

              }
    return params
