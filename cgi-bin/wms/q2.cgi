#!/bin/sh

MS_MAPFILE=/mesonet/www/apps/iemwebsite/data/wms/q2.map
export MS_MAPFILE

/mesonet/www/apps/iemwebsite/cgi-bin/mapserv/mapserv
