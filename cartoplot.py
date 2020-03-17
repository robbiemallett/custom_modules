import cartopy.crs as ccrs
import cartopy
import matplotlib.pyplot as plt
import numpy as np


def cartoplot(lon,
              lat,
              data,
              bounding_lat=65,
              land=True,
              ocean=False,
              gridlines=True,
              figsize=[10,5],
              save_dir=None,
              show=True,
              color_scale=(None,None),
              color_scheme='Plasma'):
    
    """
    Plots a north polar plot using cartopy. \
    Must be supplied with gridded arrays of lon, lat and data
    """

    # Make plot

    fig = plt.figure(figsize=figsize)
    ax = plt.axes(projection=ccrs.NorthPolarStereo())
    
    
    if ocean == True:
        ax.add_feature(cartopy.feature.OCEAN,zorder=2)
    if land == True:
        ax.add_feature(cartopy.feature.LAND, edgecolor='black',zorder=1)

    ax.set_extent([-180, 180, 90, bounding_lat], ccrs.PlateCarree())


    # extent = 2500000

    # ax.set_extent((-extent,
    #                extent,
    #                -extent,
    #                extent),
    #               crs=ccrs.NorthPolarStereo())
    
    
    if gridlines == True:
        ax.gridlines()
        
    vmin, vmax = color_scale[0], color_scale[1]

    plt.pcolormesh(np.array(lon), np.array(lat), np.array(data), vmin = vmin, vmax = vmax,
                 transform=ccrs.PlateCarree(),zorder=0)
    
    plt.colorbar()
    

        
    
    if save_dir != None:
        plt.savefig(save_dir)
        
    if show == True:
        plt.show()


# cartoplot(data['lon'],data['lat'],data['sea_ice_thickness'][0])





