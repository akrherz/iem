#!/bin/sh

MS_MAPFILE=/opt/iem/data/wms/us/obs.map
export MS_MAPFILE

/opt/miniconda3/envs/prod/bin/mapserv
