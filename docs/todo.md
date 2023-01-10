## SpiritQuest RL

Spirit Quest is a roguelike/adventure/rpg hybrid, originally based on Roguelike Tutorial Revised
and jcerise's roguelike tutorial.

Here are some main features:

- Travel between two worlds, a 'dream world' and the waking world
- Adventure in dream worlds and defeat monsters with the powers bestowed by your spirit animals
- Encounter new animals and creatures and learn their powers
- Rescue people stuck in the spirit realm and gain their aid in your mission
- Unlock the final spirit dungeon by rescuing enough lost souls

## TODO:

- ~~Handle inputs better and cleaner~~
- ~~Refactor cursor component~~
- ~~Move data to json~~
- ~~Move place_entities outside gamemap and refactor~~
- ~~Add abilities on player and give them action cost~~
- ~~Add stealth~~
- Items and inventory
- Npcs
  - make npc quests based on black sabbath modifiers
  - make rescueable npcs which come to hub and give powers/bonuses (merchant, blacksmith, herbalist, trainer, priest..)
- Quests
- ~~Level up system~~
- Saving and loading
- ~~Refactor menus to use classes~~
- Add better level generation

REFACTOR:
- Caster AI component & behavior
- remove target_self and target_other, make target an attribute under ability
- ~~Status effects under one place, remove under fighter component~~
- Check AI buffing & debuffing bugs
- ~~Tilemap & palettes -> json~~

FIX:
- ~~drain atk don't work~~
- long description names in skill upgrade menu (fly)

BUGS:
- clear enemy stats after enemy dead
- when standing on a corpse, entering menu, receiving messages from menu, corpse message shouldn't be displayed again

IDEAS:
- Unique locations: Black crow forest
- Unique monsters: Black crow king
- Add skill mutation (randomly mix parameters of two skills)
- Implement AI skill cooldown

### Alpha 0.0.1 roadmap

- All the base systems implemented:
  ~~- Combat~~
  ~~- Abilities~~
  - Sufficient AI
  - NPC system / dialogue
  ~~- Level up / character progression~~
  - Dungeon generation
  - Dungeon progression
  - Win condition
  - Split engine from assets, open-source engine & close assets
  - Saving and loading
  - Distribution (Linux, Win)
  - Itch.io release