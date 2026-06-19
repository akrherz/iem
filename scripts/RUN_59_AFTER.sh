#!/bin/bash
# Run at :59 after the hour, some stuff to get a jump on the next hour
cd ingestors/madis
python extract_hfmetar.py --hours=0 &

cd ../../plots
bash MW_mesonet.sh
bash RUN_PLOTS.sh

cd ../iemplot
bash RUN.sh
