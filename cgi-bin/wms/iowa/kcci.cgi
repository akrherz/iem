#!/bin/sh

MS_MAPFILE=/var/www/data/wms/iowa/kcci.map
export MS_MAPFILE

/var/www/cgi-bin/mapserv/mapserv
