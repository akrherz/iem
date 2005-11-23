#!/bin/sh

MS_MAPFILE=/mesonet/share/msapps/wms/nexrad/ntp.map
export MS_MAPFILE

/var/www/cgi-bin/mapserv/mapserv
