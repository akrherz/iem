#!/bin/sh

MS_MAPFILE=/opt/iem/data/wms/us/mrms.map
export MS_MAPFILE

/opt/iem/cgi-bin/mapserv/mapserv
