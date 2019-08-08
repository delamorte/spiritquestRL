def get_dngn_colors(mod):
    colors = []
    if mod >= 0:
        
        colors = ["lightest amber",
                         "lighter amber",
                         "light amber",
                         "dark amber",
                         "darker amber",
                         "darkest amber"]
        
    if mod < 0:
        colors = ["lightest gray",
                         "lighter gray",
                         "light gray",
                         "dark gray",
                         "darker gray",
                         "darkest gray"]
        
    #if mod > 0:
    #    colors = [None,
    #                     None,
    #                     None,
    #                     None,
    #                     None,
    #                     None]
        
    return colors

def get_forest_colors(mod):
    colors = []
    if mod > 0:
        colors = ["lightest orange",
                         "lighter orange",
                         "light orange",
                         "dark orange",
                         "darker orange"]
    
    if mod < 0:
        colors = ["lightest gray",
                         "lighter gray",
                         "light gray",
                         "dark gray",
                         "darker gray",
                         "darkest gray"]    
    if mod == 0:
        colors = [None,
                         None,
                         None,
                         None,
                         None,
                         None]
    return colors
