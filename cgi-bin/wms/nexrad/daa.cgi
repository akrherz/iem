#!/bin/sh

MS_MAPFILE=/opt/iem/data/wms/nexrad/daa.map
export MS_MAPFILE

/opt/iem/cgi-bin/mapserv/mapserv
