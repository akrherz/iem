#!/bin/sh

MS_MAPFILE=/var/www/data/wms/iowa/rainfall.map
export MS_MAPFILE

/var/www/cgi-bin/mapserv/mapserv
