#!/bin/sh

MS_MAPFILE=/opt/iem/data/wms/goes_east.map
export MS_MAPFILE

/opt/iem/cgi-bin/mapserv/mapserv
