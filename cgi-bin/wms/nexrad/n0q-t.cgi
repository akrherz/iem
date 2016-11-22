#!/bin/sh

MS_MAPFILE=/opt/iem/data/wms/nexrad/n0q-t.map
export MS_MAPFILE

/opt/iem/cgi-bin/mapserv/mapserv
