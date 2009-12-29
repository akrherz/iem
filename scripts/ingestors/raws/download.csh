#!/bin/csh
# Download RAWS data
# Daryl Herzmann 13 Jun 2003

wget -q -O IA_NEAL_SMITH.txt 'http://raws.wrh.noaa.gov/cgi-bin/roman/raws_flat.cgi?stn=NSWI4'
wget -q -O IA_DESOTO.txt 'http://raws.wrh.noaa.gov/cgi-bin/roman/raws_flat.cgi?stn=TR808'

grep "^IA DESOTO" IA_DESOTO.txt > desoto.dat
grep "^IA NEAL SMITH" IA_NEAL_SMITH.txt > ns.dat

./process.py desoto.dat RAWDES
./process.py ns.dat RAWNSM

rm -f ns.dat desoto.dat IA_DESOTO.txt IA_NEAL_SMITH.txt
