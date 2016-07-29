# Run at :59 after the hour, some stuff to get a jump on the next hour
cd ingestors/madis
python extract_hfmetar.py 0 &

cd ../../plots
./MW_mesonet.csh
./RUN_PLOTS

cd ../iemplot
./RUN.csh
