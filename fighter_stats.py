from components.ai import BasicMonster
from components.fighter import Fighter

def get_fighter_stats(name):

    fighter_component = None
    
    if name is 'player':
        fighter_component = Fighter(
            hp=20, ac=3, ev=3, power=3, mv_spd=1, atk_spd=1, size="normal", fov=6, abilities=[])
    elif name is 'rat':
        fighter_component = Fighter(
            hp=10, ac=1, ev=4, power=4, mv_spd=2, atk_spd=1, size="small", fov=4, abilities=["paralyzing bite"])
    elif name is 'crow':
        fighter_component = Fighter(
            hp=8, ac=1, ev=6, power=3, mv_spd=1.5, atk_spd=1, size="normal", fov=8, abilities=["swoop", "reveal"])
    elif name is 'snake':
        fighter_component = Fighter(
            hp=12, ac=1, ev=2, power=5, mv_spd=1, atk_spd=1, size="small", fov=6, abilities=["poison bite"])
    elif name is 'frog':
        fighter_component = Fighter(
            hp=20, ac=1, ev=5, power=5, mv_spd=1.5, atk_spd=1, size="normal", fov=6, abilities=["leap"])
    
    return fighter_component

def get_fighter_ai(name):
    
    ai_component = None
    
    if name is 'rat':
        ai_component = BasicMonster()
    elif name is 'crow':
        ai_component = BasicMonster()
    elif name is 'snake':
        ai_component = BasicMonster()
    elif name is 'frog':
        ai_component = BasicMonster()
    
    return ai_component