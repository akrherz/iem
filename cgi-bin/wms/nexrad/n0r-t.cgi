#!/bin/sh

MS_MAPFILE=/mesonet/share/msapps/wms/nexrad/n0r-t.map
export MS_MAPFILE

/var/www/cgi-bin/mapserv/mapserv.060623
