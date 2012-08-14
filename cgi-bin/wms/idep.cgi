#!/bin/sh

MS_MAPFILE=/mesonet/www/apps/iemwebsite/data/wms/idep.map
export MS_MAPFILE

/mesonet/www/apps/iemwebsite/cgi-bin/mapserv/mapserv
