# IEM Reanalysis

daryl can't keep the code logic of all these straight, so I had better document
this for myself!  There is also some chicken/egg stuff that goes on here, so we
shall clarify that as well.  Additionally, there are `china` and `europe` domains
at play here, so there is no hope.

## Yearly NetCDF storage

The basic storage unit of IEMRE are yearly netCDF files. You can find most of these files [here](https://mesonet.agron.iastate.edu/onsite/iemre/).  For yearly file storage, there are

| Filename | Description |
| ---- | --- |
| ${YEAR}_iemre_daily.nc | 12z and calendar day totals |
| ${YEAR}_iemre_hourly.nc | Hourly analyses |

## Daily Analysis Variable Sourcing

### high_tmpk_12z low_tmpk_12z snow_12z snowd_12z

This is done by `daily_analysis.py`. If the year is 2009+, we look to see what COOP data the IEM has archived for the date and so a simple griding of it.  Otherwise, we look to see what all observations we already have in the COOP database and grid those out.

### p01d_12z

`daily_analysis.py` sums up the hourly iemre precipitation data. For pre-1997 dates, we are gridding out whatever climodat station observations we have for the date.

### high_tmpk low_tmpk avg_dwpk wind_speed

If the year is greater than 1927, `daily_analysis.py` looks at the IEM Access database and grids out whatever observations it can find.

### p01d

`daily_analysis.py` looks at the hourly grids and constructs a midnight CST/CDT analysis.

### rsds

`grid_rsds.py` uses HRRR for 2014+ dates and grids out sampled COOP data points that can from a script in `../coop/narr_solarrad.py` and `../coop/merra_solarrad.py`.  The COOP database storage never uses this variable to drive its "daily" values, but uses the grid sampling done by the above scripts.
