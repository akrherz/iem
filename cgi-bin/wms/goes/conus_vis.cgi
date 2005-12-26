#!/bin/sh

MS_MAPFILE=/var/www/data/wms/goes/conus_vis.map
export MS_MAPFILE

/var/www/cgi-bin/mapserv/mapserv
