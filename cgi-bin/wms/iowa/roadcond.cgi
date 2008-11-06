#!/bin/sh

MS_MAPFILE=/var/www/data/wms/iowa/roadcond.map
export MS_MAPFILE

/var/www/cgi-bin/mapserv/mapserv
