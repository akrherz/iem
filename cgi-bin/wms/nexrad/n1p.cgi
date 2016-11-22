#!/bin/sh

MS_MAPFILE=/opt/iem/data/wms/nexrad/n1p.map
export MS_MAPFILE

/opt/iem/cgi-bin/mapserv/mapserv
