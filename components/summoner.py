from random import choice

from color_functions import get_monster_color
from components.abilities import Abilities
from components.ai import BasicMonster
from components.entity import get_neighbours, Entity
from components.fighter import Fighter
from components.light_source import LightSource
from components.status_effects import StatusEffects
from data import json_data
from map_objects.tilemap import tilemap
from ui.message import Message


class Summoner:
    def __init__(self, summoning=None, rank=None):
        self.owner = None
        self.summoning = summoning
        self.rank = rank
        self.summoned_entities = []

    def process(self, game_map):
        msg = None
        if not self.summoning and self.summoned_entities:
            summons = []
            for entity in self.summoned_entities:
                summons.append(entity.name)
                game_map.entities["allies"].remove(entity)
                game_map.tiles[entity.x][entity.y].remove_entity(entity)
                del entity
            self.summoned_entities = []
            self.owner.fighter.summoning = False
            self.summoning = [""]
            if len(summons) > 1:
                msg = Message("Your trusty companions {0} return back to the spirit plane!".format(", ".join(summons)))
            else:
                msg = Message("Your trusty companion {0} returns back to the spirit plane!".format(summons[0]))
            return msg

        elif self.summoning and not self.summoned_entities:
            if len(self.summoning) <= self.rank:
                name = self.summoning[-1]
            else:
                name = self.summoning[self.rank]
            char = tilemap()["monsters"][name]
            color = get_monster_color(name)
            f_data = json_data.data.fighters[name]
            remarks = f_data["remarks"]
            fighter_component = Fighter(hp=f_data["hp"], ac=f_data["ac"], ev=f_data["ev"],
                                        power=f_data["power"], mv_spd=f_data["mv_spd"],
                                        atk_spd=f_data["atk_spd"], size=f_data["size"], fov=f_data["fov"])
            ai_component = BasicMonster(ally=True)
            light_component = LightSource(radius=fighter_component.fov)
            abilities_component = Abilities(name)
            status_effects_component = StatusEffects(name)
            neighbours = get_neighbours(self.owner, game_map=game_map.tiles, radius=3, algorithm="square", empty_tiles=True)
            summon_tile = choice(neighbours)
            entity_name = "[color=amber]"+name + " (ally)" + "[color=default]"
            monster = Entity(summon_tile.x, summon_tile.y, 3, char,
                             color, entity_name, blocks=True, fighter=fighter_component, ai=ai_component,
                             light_source=light_component, abilities=abilities_component,
                             status_effects=status_effects_component, remarks=remarks, indicator_color="light green")
            monster.light_source.initialize_fov(game_map)
            game_map.tiles[summon_tile.x][summon_tile.y].add_entity(monster)
            game_map.entities["allies"].append(monster)
            self.summoned_entities.append(monster)
            msg = Message("A friendly {0} appears!".format(monster.name))
            return msg

        return msg
