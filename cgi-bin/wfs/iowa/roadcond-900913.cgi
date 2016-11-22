#!/bin/sh

MS_MAPFILE=/opt/iem/data/wfs/iowa/roadcond-900913.map
export MS_MAPFILE

/opt/iem/cgi-bin/mapserv/mapserv
