IEM Reanalysis
==============

daryl can't keep the code logic of all these straight, so I had better document
this for myself!  There is also some chicken/egg stuff that goes on here, so we
shall clarify that as well.

Yearly NetCDF storage
---------------------

The basic storage unit of IEMRE are yearly netCDF files. You can find most of these files [here](https://mesonet.agron.iastate.edu/onsite/iemre/).  For yearly file storage, there are

| Filename | Description |
| ---- | --- |
| ${YEAR}_iemre_daily.nc | 12z and calendar day totals |
| ${YEAR}_iemre_hourly.nc | Hourly analyses |

Data Flow
---------

So the confusing part is how this data gets bootstrapped and the realtime data flow into these files.

## realtime flow

