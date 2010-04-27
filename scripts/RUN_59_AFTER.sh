#!/bin/sh
# Run at :59 after the hour, some stuff to get a jump on the next hour

cd plots
./RUN_PLOTS

cd ../iemplot
./RUN.csh
