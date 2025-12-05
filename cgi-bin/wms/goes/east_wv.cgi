#!/bin/sh

MS_MAPFILE=/opt/iem/data/wms/goes/east_wv.map
export MS_MAPFILE

/opt/miniconda3/envs/prod/bin/mapserv
