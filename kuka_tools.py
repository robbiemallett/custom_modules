import numpy as np
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from pyproj import Proj, Transformer
import numpy as np
import datetime

def lonlat_to_xy(coords_1, coords_2, hemisphere, inverse=False):

 

    """Converts between longitude/latitude and EASE xy coordinates.
 
    Args:
        lon (float): WGS84 longitude
        lat (float): WGS84 latitude
        hemisphere (string): 'n' or 's'
        inverse (bool): if true, converts xy to lon/lat
 
    Returns:
        tuple: pair of xy or lon/lat values
    """

 

    EASE_Proj = {'n': 'EPSG:3408',
                 's': 'EPSG:3409'}
    
    WGS_Proj = 'EPSG:4326'
    
    for coords in [coords_1, coords_2]: assert isinstance(coords,(np.ndarray,list))

    if inverse == False: # lonlat to xy
        
        lon, lat = coords_1, coords_2
        
        transformer = Transformer.from_crs(WGS_Proj, EASE_Proj[hemisphere])
        
        x, y = transformer.transform(lat, lon)
        
        return (x, y)

    else: # xy to lonlat
        
        x, y = coords_1, coords_2
        
        transformer = Transformer.from_crs(EASE_Proj[hemisphere], WGS_Proj)
        
        lat, lon = transformer.transform(x, y)
        
        return (lon, lat)
        
def get_time_ticks(times):
    seconds = [t.second for t in times]
    hours = [t.hour for t in times]
    minutes = [t.minute for t in times]
    time_ticks = [f'{h}:{str(m).zfill(2)}:{str(s).zfill(2)}' for h,m,s in zip(hours, minutes, seconds)]
    return time_ticks

def plot_file(f,band,directory,time_offset_s=0,vlines=[]):
    
    if band.lower()=='ka':
        
        skipper = 50
        ylims = (1000,570)
        
    elif band.lower()=='ku':
        skipper=20
        ylims = (600,400)
        
    else:raise
    
    with Dataset(f'{directory}/{f}') as d:
        ranges = np.array(d['range'])
        times = np.array([datetime.datetime(1970,1,1)+datetime.timedelta(seconds=int(x))+datetime.timedelta(seconds=int(time_offset_s)) for x in d['start_time']])
        
        time_ticks = get_time_ticks(times)

        hh = np.array(d['hh_power_decon0'])
        vv = np.array(d['vv_power_decon0'])

    plt.figure(figsize=(10,4))
    plt.imshow(np.log(hh),aspect='auto')
    plt.xticks(np.arange(0,hh.shape[1],skipper),labels=time_ticks[::skipper],rotation=90)

    plt.yticks(np.arange(0,hh.shape[0],skipper),labels=ranges[::skipper])

    plt.ylim(ylims[0],ylims[1])

    for time in vlines:
        time_ind = get_time_index(time,times)
        plt.axvline(time_ind,color='k',ls='--')

def get_ymd_from_filename(filename):
    
    datestring = filename.split('Scat')[-1][:8]
    
    y = int(datestring[:4])
    m = int(datestring[4:6])
    d = int(datestring[6:8])
    
    return(y,m,d)
    
def get_time_index(time,times):
    
    deltas = np.array(times) - time

    secs = np.array([d.seconds for d in deltas])
    ms = np.array([d.microseconds for d in deltas])
    
    secs = secs + (ms * 1e-6)
    
    index = np.argmin(secs)
    
    return index


def get_range_index(input_range,ranges):
    
    deltas = np.array(ranges) - input_range
    
    index = np.argmin(np.abs(deltas))
    
    return index


def plot_pos(file,directory,plot=True,x0=0,y0=0):
    
    d = Dataset(f'{directory}/{file}')
    x, y = lonlat_to_xy(np.array(d['lon']), np.array(d['lat']),hemisphere='s')
    y = y[np.abs(x)>1] -y0
    x = x[np.abs(x)>1] -x0

    
    if plot:
        plt.scatter(x,y,marker='x',label=file[-9:-3])

    return (x,y)