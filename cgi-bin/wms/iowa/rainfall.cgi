#!/bin/sh

MS_MAPFILE=/opt/iem/data/wms/iowa/rainfall.map
export MS_MAPFILE

/opt/iem/cgi-bin/mapserv/mapserv
