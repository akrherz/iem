#!/bin/csh

set BASE="http://raws.wrh.noaa.gov/cgi-bin/roman/raws_flat.cgi?stn="

foreach ID (NWSI4 YSPI4 TR808 LSHI4 TS568 TS657 FRMI4)
  wget -q -O ${ID}.txt "${BASE}${ID}"
 ./process.py ${ID}
end
