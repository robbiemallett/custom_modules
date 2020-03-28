import numpy as np
from netCDF4 import Dataset
import pickle
import mask
import xarray as xr

def get_field(key,
                 month,
                 year,
                 variable,
                 resolution=760):

    """imports a remote sensing field. 
       key options: cci_envisat, cci_cs2, landy_cs2, w99, mw99, osisaf, snowmodel.
       variable options: rad/thickness for radar freeboard or thickness in cci/landy;
       depth,density,swe for w99/mw99; depth/density for snowmodel. Bespoke variables also available for cci/landy fields.
       variable w99 resolution available, currently automatically set to 760x1120.
       No variable required for osisaf retrieval.
       Units should all be SI base."""
    
    
    #get field
    
    if 'cci' in key.lower():
        
        if 'envisat' in key.lower():
        
            # User wants envisat field

            data_dir = f'/home/robbie/Dropbox/SM_Thickness/data/Envisat_CCI/{year}/'
            file = f'ESACCI-SEAICE-L3C-SITHICK-RA2_ENVISAT-NH25KMEASE2-{year}{month}-fv2.0.nc'
            data = Dataset(data_dir+file)
        
        elif 'cs2' in key.lower():
            
            # User wants CCI CS2 field
        
            data_dir = f'/home/robbie/Dropbox/SM_Thickness/data/CS2_CCI/{year}/'
            file = f'ESACCI-SEAICE-L3C-SITHICK-SIRAL_CRYOSAT2-NH25KMEASE2-{year}{month}-fv2.0.nc'
            data = Dataset(data_dir+file)
        
        else:
            print('Which instrument do you want?')
            return(1)
            
        
        if 'rad' in variable.lower():
            
            # Get radar freeboard
            
            lon = data['lon']
            lat = data['lat']
            field = data['radar_freeboard'][0]
            
            
        elif 'thickness' in variable.lower():
            
            # Get total thickness
            
            lon = data['lon']
            lat = data['lat']
            field = data['sea_ice_thickness']

        else:
            lon = data['lon']
            lat = data['lat']
            field = data[variable]
            
    elif 'landy' in key.lower():

        # print('landy cs2')
        
        # User wants jack landy's CS2 data
        
        data_dir = '/home/robbie/Dropbox/SM_Thickness/data/CS2_Landy/'
        file = f'ubristol_cryosat2_seaicethickness_nh25km_{year}_{month}_v1.nc'
        data = Dataset(data_dir+file)
        
        if 'rad' in variable.lower():
            # print('radar freeboard')
            # Get radar freeboard
            
            field = np.flipud(data['Radar_Freeboard'])
            
        elif 'thickness' in variable.lower():
            
            # Get total thickness

            field = np.flipud(data['Sea_Ice_Thickness'])
            
        else:
            
            # User wants some other variable. Give it to them!

            field = np.flipud(data[variable])

        lon = mask.get('lon')
        lat = mask.get('lat')

######################################################################

    elif key.lower() == 'w99':
        
        # User wants the W99 field
        # Get the W99 grid

        if resolution == 361:

            data_dir = '/home/robbie/Dropbox/SM_Thickness/data/W99/'
            
            with xr.open_dataset(f'{data_dir}W99_361.nc') as data:

                ds_month = data.where(int(month) == data.month, drop=True)

                field = np.array(ds_month[variable])[0]

            lon = mask.get('lon')
            lat = mask.get('lat')

        elif resolution == 760:

            W99_data = pickle.load(open(f"/home/robbie/Dropbox/SM_Thickness/code/W99/W99_{resolution}.p","rb"))
        
            field = W99_data[variable][int(month)]

            grid = pickle.load(open(f'/home/robbie/custom_modules/{resolution}_grid.p','rb'))
            lon = grid['lon']
            lat = grid['lat']

#######################################################################

    elif 'osisaf' in key.lower():
        
        # User wants the OSISAF ice type data
        
        data_dir = f'/home/robbie/Dropbox/SM_Thickness/data/OSISAF_type_monthlies/{resolution}/'
        file = f'{year}{month}monmean.nc'
        data = Dataset(data_dir+file)
        
        lon = data['lon']
        lat = data['lat']
        if resolution > 400:
            field = data['ice_type'][0]
        else:
            field = data['ice_type']

#######################################################################

    elif 'snowmodel' in key.lower():
        
        # User wants the SnowModel snow data
        
        # Possible variables: depth, density, SWE
 
        data_dir = '/home/robbie/Dropbox/SM_Thickness/data/SnowModel/monthly_means/'

        with xr.open_dataset(f'{data_dir}{year}{str(month).zfill(2)}.nc') as data:

            field = data[variable]
        
        lon = mask.get('lon')
        lat = mask.get('lat')

#######################################################################

    elif key.lower() == 'mw99':

        data_dir = '/home/robbie/Dropbox/SM_Thickness/data/W99/mW99_361/'

        with xr.open_dataset(f'{data_dir}{year}_mW99.nc') as data:

            ds_month = data.where(int(month) == data.month, drop=True)

            field = np.array(ds_month[variable])[0]

        lon = mask.get('lon')
        lat = mask.get('lat')

######################################################################

    elif 'nesosim' in key.lower():

        if resolution == 361:

            data_dir = '/home/robbie/Dropbox/SM_Thickness/data/nesosim/361_monthlies/'

            with xr.open_dataset(f'{data_dir}{year}{str(month).zfill(2)}.nc') as data:

                field = data[variable]

            lon = mask.get('lon')
            lat = mask.get('lat')

#######################################################################

    elif 'cds' in key.lower():
        
        # User wants cds ice type data, available between March 2002 and Dec 2005
        
        if resolution == 432:
            
            data_dir = '/home/robbie/Dropbox/SM_Thickness/data/CDS_type/monmeans/432/'
            
        elif resolution == 361:
            
            data_dir = '/home/robbie/Dropbox/SM_Thickness/data/CDS_type/monmeans/361/'
            
        file_name = f'{year}_{month}_monthlymean.nc'

        data = Dataset(data_dir+file_name)

        lon = data['lon']
        lat = data['lat']
        field = data['ice_type']

#######################################################################

    elif 'icesat' in key.lower():
        
        data_dir = '/home/robbie/Dropbox/SM_Thickness/data/ICESAT/361/'

        f_name = f'{month}_{year}_ICESAT.nc'

        data = Dataset(data_dir+f_name)

        field = data['freeboard']

        lon = data['lon']

        lat = data['lat']
        
    #return dictionary of field, lon, lat
    
    data_dict = {'field':np.array(field),
                 'lon':np.array(lon),
                 'lat':np.array(lat)}
    
    return(data_dict)
