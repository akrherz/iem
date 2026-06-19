#!/bin/bash
# Run at :59 after the hour, some stuff to get a jump on the next hour
cd ingestors/madis || exit 1
python extract_hfmetar.py --hours=0 &

cd ../../plots || exit 1
bash MW_mesonet.sh
bash RUN_PLOTS.sh

cd ../iemplot || exit 1
bash RUN.sh
