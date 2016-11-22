#!/bin/sh

MS_MAPFILE=/opt/iem/data/wms/iowa/roadcond.map
export MS_MAPFILE

/opt/iem/cgi-bin/mapserv/mapserv
