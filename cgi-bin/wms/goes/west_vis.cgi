#!/bin/sh

MS_MAPFILE=/opt/iem/data/wms/goes/west_vis.map
export MS_MAPFILE

/opt/miniconda3/envs/prod/bin/mapserv
