#!/bin/sh

MS_MAPFILE=/opt/iem/data/wms/goes/east_3.9.map
export MS_MAPFILE

/opt/iem/cgi-bin/mapserv/mapserv
