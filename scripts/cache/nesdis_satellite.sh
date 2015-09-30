#!/bin/sh
#set -x
# Get and process files from NESDIS
# channel 5 12.0um
# channel 4 10.70um
# channel 3 6.75um
# channel 2 3.9um 
# channel 1 0.65um  Vis
# EAST -110 65.5 -29 -15
# West -180 65.5 -102 -15

# Verbose for now to check some things
#date

tm=$(python ts.py $1 %j%H%M)
tm2=$(python ts2.py $1 %j%H%M)
ftm=$(python ts.py $1 %Y%m%d%H%M)
atm=$(python ts.py $1 %H%M)
wtm=$(python wdownload.py $1)
cd /mesonet/tmp
mkdir nesdis.$ftm
cd nesdis.$ftm

BASE="http://satepsanone.nesdis.noaa.gov/pub/GIS"

function getter(){
	for i in {1..10}
		do
			wget --connect-timeout=60 -O $1 -q $2 && return
			#echo "FAIL $2"
			sleep 60
			done	
}

getter GoesEast1V${tm}.tif $BASE/GOESeast/GoesEast1V_latest.tif
getter GoesEast1V${tm}.tfw $BASE/GOESeast/GoesEast1V_latest.tfw
getter GoesEast04I3${tm}.tif $BASE/GOESeast/GoesEast04I3_latest.tif
getter GoesEast04I3${tm}.tfw $BASE/GOESeast/GoesEast04I3_latest.tfw
getter GoesEast04I4${tm}.tif $BASE/GOESeast/GoesEast04I4_latest.tif
getter GoesEast04I4${tm}.tfw $BASE/GOESeast/GoesEast04I4_latest.tfw

getter GoesWest1V${tm}.tif $BASE/GOESwest/GoesWest1V_latest.tif 
getter GoesWest1V${tm}.tfw $BASE/GOESwest/GoesWest1V_latest.tfw
getter GoesWest04I3${tm}.tif $BASE/GOESwest/GoesWest04I3_latest.tif
getter GoesWest04I3${tm}.tfw $BASE/GOESwest/GoesWest04I3_latest.tfw
getter GoesWest04I4${tm}.tif $BASE/GOESwest/GoesWest04I4_latest.tif
getter GoesWest04I4${tm}.tfw $BASE/GOESwest/GoesWest04I4_latest.tfw

#ls -l *.tif
#ls -l *.tfw

# Merge Visible, please
szw=$(stat -c %s GoesWest1V${tm}.tif)
sze=$(stat -c %s GoesEast1V${tm}.tif)
if [ -e GoesEast1V${tm}.tif -a $szw -gt 1000 -a $sze -gt 1000 ]
then
	# Create composite TIF, 4km
	gdal_merge.py -q -o vis.tif  -ul_lr -126 50 -66 24 -ps 0.04 0.04 GoesWest1V${tm}.tif GoesEast1V${tm}.tif
	/home/ldm/bin/pqinsert -p "gis ac $ftm gis/images/4326/sat/conus_goes_vis4km.tif GIS/sat/conus_goes_vis4km_$atm.tif tif" vis.tif
  	# Create 1km VIS variant for Google Maps, CONUS
	gdal_merge.py -q -o vis.tif  -ul_lr -126 50 -66 24 -ps 0.01 0.01 GoesWest1V${tm}.tif GoesEast1V${tm}.tif
	rm -f vis_900913.tif >& /dev/null
	gdalwarp -q -s_srs EPSG:4326 -t_srs EPSG:3857 -tr 1000.0 1000.0 vis.tif vis_900913.tif
	/home/ldm/bin/pqinsert -p "gis c $ftm gis/images/900913/sat/conus_goes_vis1km.tif bogus tif" vis_900913.tif
	# Create full 1km VIS
	rm vis_900913.tif vis.tif >& /dev/null
	gdal_merge.py -q -o vis.tif  -ul_lr -180 65 -30 -15 -ps 0.01 0.01 GoesWest1V${tm}.tif GoesEast1V${tm}.tif
	gdalwarp -q -s_srs EPSG:4326 -t_srs EPSG:3857 -tr 1000.0 1000.0 vis.tif vis_900913.tif
	gdaladdo -q vis_900913.tif 2 4 6 18
fi

sz=$(stat -c %s GoesEast04I4${tm}.tif)
sz2=$(stat -c %s GoesWest04I4${tm}.tif)
if [ $sz -gt 1000 -a $sz2 -gt 1000 ]
then
	gdal_merge.py -q -o ir.tif  -ul_lr -126 50 -66 24 -ps 0.04 0.04 GoesWest04I4${tm}.tif GoesEast04I4${tm}.tif
	/home/ldm/bin/pqinsert -p "gis ac $ftm gis/images/4326/sat/conus_goes_ir4km.tif GIS/sat/conus_goes_ir4km_$atm.tif tif" ir.tif
	# Create 4km IR variant for Google Maps
	rm -f ir_900913.tif >& /dev/null
	gdalwarp -q -s_srs EPSG:4326 -t_srs EPSG:3857 -tr 4000.0 4000.0 ir.tif ir_900913.tif
	/home/ldm/bin/pqinsert -p "gis c $ftm gis/images/900913/sat/conus_goes_ir4km.tif bogus tif" ir_900913.tif
    # Full res!
	rm ir_900913.tif ir.tif >& /dev/null
	gdal_merge.py -q -o ir.tif  -ul_lr -180 65 -30 -15 -ps 0.04 0.04 GoesWest04I4${tm}.tif GoesEast04I4${tm}.tif
	gdalwarp -q -s_srs EPSG:4326 -t_srs EPSG:3857 -tr 4000.0 4000.0 ir.tif ir_900913.tif
	gdaladdo -q ir_900913.tif 2 4 6 18
fi

sz=$(stat -c %s GoesEast04I3${tm}.tif)
sz2=$(stat -c %s GoesWest04I3${tm}.tif)
if [ $sz -gt 1000 -a $sz2 -gt 1000 ]
then
	gdal_merge.py -q -o wv.tif  -ul_lr -126 50 -66 24 -ps 0.04 0.04 GoesWest04I3${tm}.tif GoesEast04I3${tm}.tif
	/home/ldm/bin/pqinsert -p "gis ac $ftm gis/images/4326/sat/conus_goes_wv4km.tif GIS/sat/conus_goes_wv4km_$atm.tif tif" wv.tif
	# Create 4km WV variant for Google Maps
	rm -f wv_900913.tif >& /dev/null
	gdalwarp -q -s_srs EPSG:4326 -t_srs EPSG:3857 -tr 4000.0 4000.0 wv.tif wv_900913.tif
	/home/ldm/bin/pqinsert -p "gis c $ftm gis/images/900913/sat/conus_goes_wv4km.tif bogus tif" wv_900913.tif
    # Full res!
	rm wv_900913.tif wv.tif >& /dev/null
	gdal_merge.py -q -o wv.tif  -ul_lr -180 65 -30 -15 -ps 0.04 0.04 GoesWest04I3${tm}.tif GoesEast04I3${tm}.tif
	gdalwarp -q -s_srs EPSG:4326 -t_srs EPSG:3857 -tr 4000.0 4000.0 wv.tif wv_900913.tif
	gdaladdo -q wv_900913.tif 2 4 6 18
fi

/home/ldm/bin/pqinsert -i -p "gis c ${ftm} gis/images/4326/goes/west1V_0.tif bogus tif" GoesWest1V${tm}.tif
/home/ldm/bin/pqinsert -i -p "gis c ${ftm} gis/images/4326/goes/west1V_0.tfw bogus tfw" GoesWest1V${tm}.tfw
/home/ldm/bin/pqinsert -i -p "gis c ${ftm} gis/images/4326/goes/east1V_0.tif bogus tif" GoesEast1V${tm}.tif
/home/ldm/bin/pqinsert -i -p "gis c ${ftm} gis/images/4326/goes/east1V_0.tfw bogus tfw" GoesEast1V${tm}.tfw

/home/ldm/bin/pqinsert -i -p "gis c ${ftm} gis/images/4326/goes/west04I4_0.tif bogus tif" GoesWest04I4${tm}.tif
/home/ldm/bin/pqinsert -i -p "gis c ${ftm} gis/images/4326/goes/west04I4_0.tfw bogus tfw" GoesWest04I4${tm}.tfw
/home/ldm/bin/pqinsert -i -p "gis c ${ftm} gis/images/4326/goes/east04I4_0.tif bogus tif" GoesEast04I4${tm}.tif
/home/ldm/bin/pqinsert -i -p "gis c ${ftm} gis/images/4326/goes/east04I4_0.tfw bogus tfw" GoesEast04I4${tm}.tfw
 
/home/ldm/bin/pqinsert -i -p "gis c ${ftm} gis/images/4326/goes/west04I3_0.tif bogus tif" GoesWest04I3${tm}.tif
/home/ldm/bin/pqinsert -i -p "gis c ${ftm} gis/images/4326/goes/west04I3_0.tfw bogus tfw" GoesWest04I3${tm}.tfw
/home/ldm/bin/pqinsert -i -p "gis c ${ftm} gis/images/4326/goes/east04I3_0.tif bogus tif" GoesEast04I3${tm}.tif
/home/ldm/bin/pqinsert -i -p "gis c ${ftm} gis/images/4326/goes/east04I3_0.tfw bogus tfw" GoesEast04I3${tm}.tfw


if [ -e vis_900913.tif ]
  	then
		/home/ldm/bin/pqinsert -i -p "gis c ${ftm} gis/images/900913/goes/vis_0.tif bogus tif" vis_900913.tif
    fi
  	
if [ -e ir_900913.tif ]
  	then
		/home/ldm/bin/pqinsert -i -p "gis c ${ftm} gis/images/900913/goes/ir_0.tif bogus tif" ir_900913.tif
    fi
  	
if [ -e wv_900913.tif ]
  	then
		/home/ldm/bin/pqinsert -i -p "gis c ${ftm} gis/images/900913/goes/wv_0.tif bogus tif" wv_900913.tif
    fi 

# Cleanup!
cd ..
rm -rf nesdis.$ftm

#DONE