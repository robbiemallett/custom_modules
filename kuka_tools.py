import numpy as np
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from pyproj import Proj, Transformer
import numpy as np
import math
import pandas as pd
import tqdm
import datetime
from scipy.stats import pearsonr

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
        
def get_nrcs(d,freq,minrange=1.3,maxrange=2):
    samples = np.array([d['vv_power_decon0'],
                        d['hv_power_decon0'],
                        d['vh_power_decon0'],
                        d['hh_power_decon0']])
    
    vars = get_vars(d,freq)
    
    tiled_range = np.tile(d['range'],(samples.shape[-1],1)).T
    gate0,gate1=get_range_index(minrange,np.array(d['range'])),get_range_index(maxrange,np.array(d['range']))
    
    range_centroid_vv = sum(tiled_range[gate0:gate1]*samples[0][gate0:gate1])/sum(samples[0][gate0:gate1])
    range_centroid_hh = sum(tiled_range[gate0:gate1]*samples[-1][gate0:gate1])/sum(samples[0][gate0:gate1])
    
    range_centroid_signal=(range_centroid_vv+range_centroid_hh)/2
    
    scale_factor=8*np.log(2)*range_centroid_signal**2*vars['corner_sigma']*math.cos(0)/(math.pi*vars['corner_range_file']**4*vars['antenna_beamwidth_rad']**2)/vars['corr_cal']
    
    total_power = np.array([np.nansum(samples[j,gate0:gate1],axis=0) for j in np.arange(4)])
    pratio = np.array([total_power[j]/vars['cr_power'][j] for j in np.arange(4)])
    nrcs=scale_factor*pratio

    corrs = calc_corrs(d,minrange-0.3,maxrange+2)
    nrcs_dict={'vv':nrcs[0],'hv':nrcs[1],'vh':nrcs[2],'hh':nrcs[3],'corr':corrs}
    return nrcs_dict

def calc_corrs(d,minrange,maxrange):
    r = np.array(d['range'])
    try:
        p = np.array(d['vv_power_decon0'])
    except:
        p = np.array(d['vv_power'])
    
    minrange = get_range_index(1,r)
    maxrange = get_range_index(4,r)
    
    corrs = np.ones(p.shape[1])
    for i in np.arange(0,p.shape[1]-1):
        ts1 = p[minrange:maxrange,i]
        ts2 = p[minrange:maxrange,i+1]
        corrs[i] = pearsonr(ts1,ts2)[0]
    return corrs

def get_corrs(filename,directory,minrange,maxrange):
    
    d = Dataset(f'{directory}/{filename}')
    corrs = calc_corrs(d,minrange,maxrange)
        
    return corrs
    
def make_nrcs_file(f,directory,target_directory,hemisphere,minrange=1.3,maxrange=2):
    d = Dataset(f'{directory}/{f}')
    
    if 'ka-scat' in f.lower():
        freq = 'ka'
    elif 'ku-scat' in f.lower():
        freq = 'ku'
    else:raise
    
    data = get_nrcs(d,freq,minrange=minrange,maxrange=maxrange)
    
    data_dict = {pol:np.array(data[pol]) for pol in ['vv','hh','hv','vh','corr']}
    
    lon = np.array(d['lon'])
    lat = np.array(d['lat'])
    
    data_dict['lon'],data_dict['lat']=lon,lat
    
    data_dict['x'],data_dict['y'] = lonlat_to_xy(lon,lat,hemisphere=hemisphere)
    
    data_dict['cross_tilt']=np.array(d['cross_tilt'])
    data_dict['along_tilt']=np.array(d['along_tilt'])
    data_dict['time']=np.array(d['start_time'])
    
    df = pd.DataFrame(data_dict)

#    df['corr'] = get_corrs(f,directory,1,4)
    
    df.to_csv(f'{target_directory}/{f[:-3]}.csv')

def get_vars(d,freq):
    
    if freq.lower()=='ku':
        corner_sigma=16.77
        antenna_beamwidth=16.9
    elif freq.lower()=='ka':
        corner_sigma=91.35
        antenna_beamwidth=11.9
    else:
        raise
        
    antenna_beamwidth_rad = math.radians(antenna_beamwidth)
    
    calvars=d['calvars']
    
    total_corner_power_vv_file = 10**(calvars.corner_reflector_vv_power_dbm/10.)
    total_corner_power_hh_file= 10**(calvars.corner_reflector_hh_power_dbm/10.)
    reference_calibration_loop_power_file = 10**(calvars.cal_peak_dbm/10.) 
    corner_range_file = calvars.corner_reflector_range_m
    
    cr_power = [total_corner_power_vv_file, 
           (total_corner_power_vv_file+total_corner_power_hh_file)/2,
           (total_corner_power_vv_file+total_corner_power_hh_file)/2,
           total_corner_power_hh_file]
    
    reference_calibration_loop_power_file = 10**(d.groups['calvars'].cal_peak_dbm/10.) 
    current_calibration_loop_power = d.current_calibration_loop_power
    corr_cal = current_calibration_loop_power/reference_calibration_loop_power_file

    vars = {'cr_power':cr_power,
            'corner_sigma':corner_sigma,
            'corner_range_file':corner_range_file,
            'antenna_beamwidth_rad':antenna_beamwidth_rad,
            'corr_cal':corr_cal}
    
    return vars
    
def get_time_ticks(times):
    seconds = [t.second for t in times]
    hours = [t.hour for t in times]
    minutes = [t.minute for t in times]
    time_ticks = [f'{h}:{str(m).zfill(2)}:{str(s).zfill(2)}' for h,m,s in zip(hours, minutes, seconds)]
    return time_ticks


def plot_file(f,band,directory,time_offset_s=0,vlines=[],set_skipper=None,ax=None):
    
    if band.lower()=='ka':
        
        skipper = 50
        ylims = (1000,570)
        
    elif band.lower()=='ku':
        skipper=20
        ylims = (600,400)
    else:raise
    if set_skipper:
        skipper=set_skipper
    
    with Dataset(f'{directory}/{f}') as d:
        ranges = np.array(d['range'])
        times = np.array([datetime.datetime(1970,1,1)+datetime.timedelta(seconds=int(x))+datetime.timedelta(seconds=int(time_offset_s)) for x in d['start_time']])
        time_ticks = get_time_ticks(times)

        hh = np.array(d['hh_power_decon0'])
        vv = np.array(d['vv_power_decon0'])
    
    if not ax:
        fig, ax = plt.subplots(1,1,figsize=(10,4))
    ax.set_ylabel('Range (m)')
    ax.set_xlabel('Time (UTC)')
    ax.set_title(f'{band} {f}',fontsize='x-large')
    ax.imshow(np.log(hh),aspect='auto')
    
    ax.set_xticks(np.arange(0,hh.shape[1],skipper),labels=time_ticks[::skipper],rotation=90)
    ax.set_yticks(np.arange(0,hh.shape[0],skipper),labels=np.round(ranges[::skipper],decimals=2))
    ax.set_ylim(ylims[0],ylims[1])
    
    time_inds=[]
    for time in vlines:
        time_ind = get_time_index(time,times)
        ax.axvline(time_ind,color='k',ls='--')
        time_inds.append(time_ind)
    return time_inds

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


def plot_pos(file,directory,plot=True,x0=0,y0=0,ax=None):
    
    d = Dataset(f'{directory}/{file}')
    x, y = lonlat_to_xy(np.array(d['lon']), np.array(d['lat']),hemisphere='s')
    y = y[np.abs(x)>1] -y0
    x = x[np.abs(x)>1] -x0


    if plot:
        if ax:
            pass
        else:
            fig,ax=plt.subplots(1,1)
        ax.scatter(x,y,marker='x',label=file[-9:-3])

    return (x,y)
