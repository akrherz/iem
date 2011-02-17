#!/bin/sh

MS_MAPFILE=/mesonet/www/apps/iemwebsite/data/wms/us/wwa.map
export MS_MAPFILE

/mesonet/www/apps/iemwebsite/cgi-bin/mapserv/mapserv
