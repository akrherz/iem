#!/bin/sh
echo -e "Content-type: text/plain\n\n"
echo -e "\n"
exit 0

MS_MAPFILE=/mesonet/www/apps/iemwebsite/data/wms/nexrad/n0r-t.map
export MS_MAPFILE

/mesonet/www/apps/iemwebsite/cgi-bin/mapserv/mapserv
