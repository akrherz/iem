#!/bin/sh

MS_MAPFILE=/mesonet/msapps/wms/nexrad/n0r.map
export MS_MAPFILE

/mesonet/www/cgi-bin/mapserv/mapserv
