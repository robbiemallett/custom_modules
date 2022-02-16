import numpy as np
import matplotlib.pyplot as plt
from cartoplot import cartoplot
import imageio
from netCDF4 import Dataset
import pickle

def get(string):
    """
                    "Lakes":0,
                    "Oceans":1,
                    "Okhotsk":2,
                    "Bering":3,
                    "Hudson":4,
                    "St Lawrence":5,
                    "Baffin":6,
                    "Greenland":7,
                    "Barents":8,
                    "Kara":9,
                    "Laptev":10,
                    "East Siberian":11,
                    "Chukchi":12,
                    "Beaufort":13,
                    "Canadian Archipelago":14,
                    "Central Arctic":15,
                    "Land":20,
                    "Coast":21}
    """
    path_grid = "/home/robbie/Dropbox/Data/grid.nc"

    if string == 'lon':
        grid_data = Dataset(path_grid)
        lon = np.array(grid_data.variables["lon"])
        return(lon)
    elif string == 'lat':
        grid_data = Dataset(path_grid)
        lat = np.array(grid_data.variables["lat"])
        return(lat)
    elif string == 'mask':
        im = imageio.imread('J_Mask.tif')
        mask = np.flipud(np.array(im))
        return(mask)

def EASE():
    """
                    "Lakes":0,
                    "Oceans":1,
                    "Okhotsk":2,
                    "Bering":3,
                    "Hudson":4,
                    "St Lawrence":5,
                    "Baffin":6,
                    "Greenland":7,
                    "Barents":8,
                    "Kara":9,
                    "Laptev":10,
                    "East Siberian":11,
                    "Chukchi":12,
                    "Beaufort":13,
                    "Canadian Archipelago":14,
                    "Central Arctic":15,
                    "Land":20,
                    "Coast":21}
    """
    mask = pickle.load( open( "/home/robbie/Dropbox/Code/mask_348x348.p", "rb" ) )
    return(mask)

def OSISAF():
    """
                    "Lakes":0,
                    "Oceans":1,
                    "Okhotsk":2,
                    "Bering":3,
                    "Hudson":4,
                    "St Lawrence":5,
                    "Baffin":6,
                    "Greenland":7,
                    "Barents":8,
                    "Kara":9,
                    "Laptev":10,
                    "East Siberian":11,
                    "Chukchi":12,
                    "Beaufort":13,
                    "Canadian Archipelago":14,
                    "Central Arctic":15,
                    "Land":20,
                    "Coast":21}
    """
    mask = pickle.load( open( "/home/robbie/custom_modules/mask_1120x760.p", "rb" ) )
    return(mask)

def plot(region_string):

    regions_dict = {"Lakes":0,
                    "Oceans":1,
                    "Okhotsk":2,
                    "Bering":3,
                    "Hudson":4,
                    "St Lawrence":5,
                    "Baffin":6,
                    "Greenland":7,
                    "Barents":8,
                    "Kara":9,
                    "Laptev":10,
                    "East Siberian":11,
                    "Chukchi":12,
                    "Beaufort":13,
                    "Canadian Archipelago":14,
                    "Central Arctic":15,
                    "Land":20,
                    "Coast":21}

    code = regions_dict[region_string]

    fig = plt.figure(figsize=(10, 8))

    cartoplot(get('lon'), get('lat'), get('mask'),color_scale=(code+1,code-1))
    
    print(code)
    
    plt.show()
