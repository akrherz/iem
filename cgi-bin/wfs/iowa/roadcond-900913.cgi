#!/bin/sh

MS_MAPFILE=/var/www/data/wfs/iowa/roadcond-900913.map
export MS_MAPFILE

/var/www/cgi-bin/mapserv/mapserv
