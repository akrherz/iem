#!/bin/sh

MS_MAPFILE=/mesonet/www/apps/iemwebsite/data/wms/goes/east_vis.map
export MS_MAPFILE

/mesonet/www/apps/iemwebsite/cgi-bin/mapserv/mapserv
