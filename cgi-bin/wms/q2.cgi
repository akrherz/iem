#!/bin/sh

MS_MAPFILE=/var/www/data/wms/q2.map
export MS_MAPFILE

/var/www/cgi-bin/mapserv/mapserv
