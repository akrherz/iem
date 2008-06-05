#!/bin/sh
exit 0

MS_MAPFILE=/var/www/data/wms/nexrad/n0r.map
export MS_MAPFILE

/var/www/cgi-bin/mapserv/mapserv
