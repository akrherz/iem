#!/bin/sh

MS_MAPFILE=/var/www/data/wms/us/wwa.map
export MS_MAPFILE

/var/www/cgi-bin/mapserv/mapserv
