#!/bin/sh

MS_MAPFILE=/opt/iem/data/wms/nexrad/eet.map
export MS_MAPFILE

/opt/miniconda3/envs/prod/bin/mapserv
