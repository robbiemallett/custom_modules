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
              hem='n',
              color_scale=(None,None),
              color_scheme='plasma'):
    
    """
    Plots a north polar plot using cartopy. \
    Must be supplied with gridded arrays of lon, lat and data
    """

    # Make plot

    fig = plt.figure(figsize=figsize)
    
    if hem == 'n':
        proj = ccrs.NorthPolarStereo()
        maxlat=90
    elif hem =='s':
        proj = ccrs.SouthPolarStereo()
        maxlat=-90
    else:
        raise
        
    ax = plt.axes(projection=proj)
    
    
    if ocean == True:
        ax.add_feature(cartopy.feature.OCEAN,zorder=2)
    if land == True:
        ax.add_feature(cartopy.feature.LAND, edgecolor='black',zorder=1)

    ax.set_extent([-180, 180, maxlat, bounding_lat], ccrs.PlateCarree())
    
    if gridlines == True:
        ax.gridlines()
        
    vmin, vmax = color_scale[0], color_scale[1]

    m = ax.pcolormesh(np.array(lon), np.array(lat),
                      np.array(data),
                      vmin = vmin,
                      vmax = vmax,
                     transform=ccrs.PlateCarree(),
                      zorder=0,cmap=color_scheme)
    
    fig.colorbar(m)
