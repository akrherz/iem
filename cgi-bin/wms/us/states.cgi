#!/bin/sh

MS_MAPFILE=/opt/iem/data/wms/political.map
export MS_MAPFILE

/opt/iem/cgi-bin/mapserv/mapserv
