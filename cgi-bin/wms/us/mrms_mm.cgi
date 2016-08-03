#!/bin/sh

MS_MAPFILE=/mesonet/www/apps/iemwebsite/data/wms/us/mrms_mm.map
export MS_MAPFILE

/mesonet/www/apps/iemwebsite/cgi-bin/mapserv/mapserv
