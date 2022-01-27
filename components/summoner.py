from random import choice

from color_functions import get_monster_color
from components.abilities import Abilities
from components.AI.ai_basic import AIBasic
from components.animation import Animation
from components.animations import Animations
from components.entity import Entity
from components.fighter import Fighter
from components.light_source import LightSource
from components.status_effects import StatusEffects
from data import json_data
from map_objects.tilemap import tilemap
from ui.message import Message


class Summoner:
    def __init__(self, rank=None):
        self.owner = None
        self.summoning = False
        self.rank = rank
        self.summoned_entities = []

    def process(self, game_map):
        msgs = []
        if self.owner.status_effects.has_effect("summoning"):
            self.summoning = True
        else:
            self.summoning = False

        if not self.summoning and self.summoned_entities:
            msgs = self.end_summoning(game_map)

        elif self.summoning and not self.summoned_entities:
            name = None
            for effect in self.owner.status_effects.items:
                if effect.summon:
                    name = effect.summon[effect.rank]
            if not name:
                return msgs
            char = tilemap()["monsters"][name]
            color = get_monster_color(name)
            f_data = json_data.data.fighters[name]
            remarks = f_data["remarks"]
            fighter_component = Fighter(hp=f_data["hp"], ac=f_data["ac"], ev=f_data["ev"],
                                        atk=f_data["atk"], mv_spd=f_data["mv_spd"],
                                        atk_spd=f_data["atk_spd"], size=f_data["size"], fov=f_data["fov"])
            ai_component = AIBasic(ally=True)
            light_component = LightSource(radius=fighter_component.fov)
            abilities_component = Abilities(name)
            status_effects_component = StatusEffects(name)
            animations_component = Animations()
            neighbours = game_map.get_neighbours(self.owner, radius=1, algorithm="square", empty_tiles=True)
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
            msg = Message("A friendly {0} appears!".format(entity_name), style="xtra")
            msgs.append(msg)
            monster.remark(random=False)
            return msgs

        return msgs

    def end_summoning(self, game_map):
        summons = []
        msgs = []
        for entity in self.summoned_entities:
            summons.append(entity.name)
            game_map.entities["allies"].remove(entity)
            game_map.tiles[entity.x][entity.y].remove_entity(entity)
            entity.dead = True
        self.summoned_entities = []
        self.summoning = False
        item = self.owner.status_effects.get_item("summoning")
        self.owner.status_effects.remove_item(item)
        if len(summons) > 1:
            msg = Message("Your trusty companions {0} return back to the spirit plane!".format(", ".join(summons)), style="xtra")
        else:
            msg = Message("Your trusty companion {0} returns back to the spirit plane!".format(summons[0]), style="xtra")
        msgs.append(msg)
        return msgs
