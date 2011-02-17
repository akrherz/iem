#!/bin/sh

MS_MAPFILE=/mesonet/www/apps/iemwebsite/data/wms/goes/west_vis.map
export MS_MAPFILE

/mesonet/www/apps/iemwebsite/cgi-bin/mapserv/mapserv
