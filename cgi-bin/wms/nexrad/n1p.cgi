#!/bin/sh

MS_MAPFILE=/mesonet/msapps/wms/nexrad/n1p.map
export MS_MAPFILE

/mesonet/www/cgi-bin/mapserv/mapserv
