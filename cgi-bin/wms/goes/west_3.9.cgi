#!/bin/sh

MS_MAPFILE=/opt/iem/data/wms/goes/west_3.9.map
export MS_MAPFILE

/opt/iem/cgi-bin/mapserv/mapserv
