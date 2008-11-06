#!/bin/sh

MS_MAPFILE=/var/www/data/wms/us/roadtemps.map
export MS_MAPFILE

/var/www/cgi-bin/mapserv/mapserv
