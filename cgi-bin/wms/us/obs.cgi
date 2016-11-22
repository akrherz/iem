#!/bin/sh

MS_MAPFILE=/opt/iem/data/wms/us/obs.map
export MS_MAPFILE

/opt/iem/cgi-bin/mapserv/mapserv
