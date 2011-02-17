#!/bin/sh

MS_MAPFILE=/mesonet/www/apps/iemwebsite/data/wms/goes/conus_wv.map
export MS_MAPFILE

/mesonet/www/apps/iemwebsite/cgi-bin/mapserv/mapserv
