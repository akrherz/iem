#!/bin/bash


if [ "${HTTP_REFERER:-aaaa}" == "http://hisz.rsoe.hu/alertmap/index2.php?area=usa" ]; then
  echo -e "Content-type: text/plain\n\n"
  echo -e "\n"
  exit 0
fi
if [ "${HTTP_REFERER:-aaaa}" == "http://hisz.rsoe.hu/alertmap/index2.php?area=usa&lang=eng" ]; then
  echo -e "Content-type: text/plain\n\n"
  echo -e "\n"
  exit 0
fi

MS_MAPFILE=/mesonet/www/apps/iemwebsite/data/wms/nexrad/n0r.map
export MS_MAPFILE

/mesonet/www/apps/iemwebsite/cgi-bin/mapserv/mapserv
