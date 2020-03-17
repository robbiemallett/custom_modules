from scipy.interpolate import griddata
import pyproj as proj
import numpy as np

args = proj.Proj(proj="aeqd", lat_0=90, lon_0=0, datum="WGS84", units="m")

crs_wgs = proj.Proj(init='epsg:4326')  # assuming you're using WGS84 geographic

def regrid(data_in,
           lon_in,
           lat_in,
           lon_out,
           lat_out,
           method='nearest'):

    xout, yout = proj.transform(crs_wgs, args, np.array(lon_out),np.array(lat_out))

    xin, yin = proj.transform(crs_wgs, args, np.array(lon_in),np.array(lat_in))

    output = griddata((xin.ravel(),yin.ravel()),
                    np.array(data_in).ravel(),
                    (xout,yout),
                    method=method)
    
    return(output)
