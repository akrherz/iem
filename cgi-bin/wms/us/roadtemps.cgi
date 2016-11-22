#!/bin/sh

MS_MAPFILE=/opt/iem/data/wms/us/roadtemps.map
export MS_MAPFILE

/opt/iem/cgi-bin/mapserv/mapserv
