from random import choice

from color_functions import get_monster_color
from components.abilities import Abilities
from components.ai import BasicMonster
from components.animations import Animations
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
        msgs = []
        if not self.summoning and self.summoned_entities:
            msgs = self.end_summoning(game_map)

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
            animations_component = Animations()
            neighbours = get_neighbours(self.owner, game_map=game_map.tiles, radius=1, algorithm="square", empty_tiles=True)
            summon_tile = choice(neighbours)
            entity_name = name + " (ally)"
            monster = Entity(summon_tile.x, summon_tile.y, 3, char,
                             color, entity_name, blocks=True, fighter=fighter_component, ai=ai_component,
                             light_source=light_component, abilities=abilities_component,
                             status_effects=status_effects_component, remarks=remarks, indicator_color="light green",
                             animations=animations_component)
            monster.light_source.initialize_fov(game_map)
            game_map.tiles[summon_tile.x][summon_tile.y].add_entity(monster)
            game_map.entities["allies"].append(monster)
            self.summoned_entities.append(monster)
            msg = Message("A friendly {0} appears!".format(entity_name))
            msgs.append(msg)
            remark_str = "{0}: {1}".format(monster.colored_name, choice(monster.remarks))
            remark_msg = Message(msg=remark_str, style="dialog")
            msgs.append(remark_msg)
            return msgs

        return msgs

    def end_summoning(self, game_map):
        summons = []
        msgs = []
        for entity in self.summoned_entities:
            summons.append(entity.name)
            game_map.entities["allies"].remove(entity)
            game_map.tiles[entity.x][entity.y].remove_entity(entity)
            del entity
        self.summoned_entities = []
        self.owner.fighter.summoning = False
        for effect in self.owner.fighter.effects:
            if effect == "summoning":
                self.owner.fighter.effects.remove(effect)
        for item in self.owner.status_effects.items:
            if item.name == "summon":
                self.owner.status_effects.remove_item(item)
        self.summoning = None
        if len(summons) > 1:
            msg = Message("Your trusty companions {0} return back to the spirit plane!".format(", ".join(summons)))
        else:
            msg = Message("Your trusty companion {0} returns back to the spirit plane!".format(summons[0]))
        msgs.append(msg)
        return msgs
