#!/bin/sh

MS_MAPFILE=/mesonet/msapps/wms/nexrad/ntp.map
export MS_MAPFILE

/mesonet/www/cgi-bin/mapserv/mapserv
