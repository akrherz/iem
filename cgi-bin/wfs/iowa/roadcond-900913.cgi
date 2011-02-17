#!/bin/sh

MS_MAPFILE=/mesonet/www/apps/iemwebsite/data/wfs/iowa/roadcond-900913.map
export MS_MAPFILE

/mesonet/www/apps/iemwebsite/cgi-bin/mapserv/mapserv
