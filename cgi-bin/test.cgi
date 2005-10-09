#!/bin/sh

MS_MAPFILE=/mesonet/www/html/GIS/apps/rainfall/wms.map
export MS_MAPFILE

/mesonet/www/cgi-bin/mapserv/mapserv.460
