#!/bin/sh

MS_MAPFILE=/mesonet/www/apps/iemwebsite/data/wms/iowa/roadcond.map
export MS_MAPFILE

/mesonet/www/apps/iemwebsite/cgi-bin/mapserv/mapserv
