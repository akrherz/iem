#!/bin/sh

MS_MAPFILE=/opt/iem/data/wms/goes/east_ir.map
export MS_MAPFILE

/opt/iem/cgi-bin/mapserv/mapserv
