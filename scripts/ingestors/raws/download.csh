#!/bin/csh

set BASE="http://raws.wrh.noaa.gov/cgi-bin/roman/raws_flat.cgi?stn="

foreach ID (NSWI4 YSPI4 LSHI4 FRMI4 HITI4 SSFI4 BKTI4)
  wget -q -O ${ID}.txt "${BASE}${ID}"
  python process.py ${ID}
end
