#!/bin/sh

MS_MAPFILE=/mesonet/www/apps/iemwebsite/data/wms/goes/conus_ir.map
export MS_MAPFILE

/mesonet/www/apps/iemwebsite/cgi-bin/mapserv/mapserv
