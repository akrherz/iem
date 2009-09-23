#!/bin/sh

wget -q -O /tmp/squaw.txt "http://waterdata.usgs.gov/ia/nwis/uv?dd_cd=01&format=rdb&period=2&site_no=05470500"

./ingestFlow.py
