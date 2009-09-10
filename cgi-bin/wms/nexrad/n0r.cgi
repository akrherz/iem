#!/bin/bash


#if [ "${HTTP_REFERER:-aaaa}" == "http://www.whnt.com/weather/" ]; then
#  echo -e "Content-type: text/plain\n\n"
#  echo -e "\n"
#  exit 0
#fi

MS_MAPFILE=/var/www/data/wms/nexrad/n0r.map
export MS_MAPFILE

/var/www/cgi-bin/mapserv/mapserv
