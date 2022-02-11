# custom_modules

Useful bits of code that I want access to from all projects

Plotting, regridding, transforming, region masking

### Cartoplot.py

I use cartoplot for rapidly visualising arrayed data for the Arctic. It goes like this:
```
from cartoplot import cartoplot

cartoplot(lon,lat,data)
```
Where all inputs are arrays and data is one-shorter in both dimensions than the coordinates. You can specify some stuff with the keywords.

### Mask.py

Allows masking into different Arctic regions using the MASIE grid.

Will get to cleaning up and documenting this soon hopefully, but it relies on mask.nc file

### ll_xy.py

Converts lon/lat coordinates to xy coords with units of meters specified in the NSIDC ease grid (Lambert equal area). Super useful for calculating the distance between points. This code also uses the most recent version of pyproj which has the Transformer syntax, which lots of people haven't yet switched to (so may be a useful template). 

### regrid.py

I use this all the time, it just regrids data. Eg. polar stereographic to EASE. It takes the lon/lat coordinates of your original data (plus the data itself), and the target lon/lats, and converts. To do this it converts all the points to xy, because otherwise the warped space of lon/lat coordinates fucks things up. Just a wrapper for scipy.griddata really, but handles the lon/lat issue conveniently. 
