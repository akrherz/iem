# Run at :59 after the hour, some stuff to get a jump on the next hour
cd ingestors/madis
python extract_hfmetar.py --hours=0 &

cd ../../plots
sh MW_mesonet.sh
csh RUN_PLOTS

cd ../iemplot
csh RUN.csh
