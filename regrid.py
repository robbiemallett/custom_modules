from scipy.interpolate import griddata
import pyproj as proj
import numpy as np
from scipy.spatial import Delaunay
from scipy.interpolate import LinearNDInterpolator
import tqdm

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


def regrid_fast(data_in,
           lon_in,
           lat_in,
           lon_out,
           lat_out,
           fill_val=np.nan):

    xout, yout = proj.transform(crs_wgs, args, np.array(lon_out),np.array(lat_out))

    xin, yin = proj.transform(crs_wgs, args, np.array(lon_in),np.array(lat_in))

    points = np.column_stack((xin.ravel(),yin.ravel()))
    tri = Delaunay(points)  # Compute the triangulation

    output = np.full((data_in.shape[0],xout.shape[0],xout.shape[1]),fill_val)    
    
    for i in tqdm.trange(0,data_in.shape[0]):

        interpolator = LinearNDInterpolator(tri, data_in[i].ravel())

        output[i] = interpolator((xout,yout))
    
    return(output)
