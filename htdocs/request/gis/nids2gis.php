<?php

$extents = Array(
 "ABR" => "42.45;-101.40;48.45;-95.40",
 "ARX" => "40.82;-94.18;46.82;-88.18",
 "DMX" => "38.72;-96.72;44.72;-90.72",
 "DVN" => "38.60;-93.57;44.60;-87.57",
 "EAX" => "35.80;-97.25;41.80;-91.25",
 "FSD" => "40.58;-99.72;46.58;-93.72",
 "MPX" => "41.83;-96.55;47.83;-90.55",
 "OAX" => "38.32;-99.37;44.32;-93.37",
 "UDX" => "41.12;-105.82;47.12;-99.82"
);

$luts = Array(
 "N0R" => "iem_n0r.tbl",
 "N1R" => "iem_n0r.tbl",
 "N2R" => "iem_n0r.tbl",
 "N3R" => "iem_n0r.tbl",
 "NCR" => "iem_n0r.tbl",
 "NVL" => "iem_n0r.tbl",
 "NTP" => "upc_ntp.tbl",
 "N1P" => "upc_n1p.tbl",
);

@mkdir("/tmp/nids2gis");
chdir("/tmp/nids2gis");
$prod = substr($_GET['prod'], 0, 3);
$ts = substr($_GET['fp'], 6,6) ."/". substr($_GET['fp'],13,4);
$fp = $prod . substr($_GET['fp'], 3);
$epsg = isset($_GET['epsg']) ? $_GET['epsg'] : '4326';
$frmt = isset($_GET['frmt']) ? $_GET['frmt'] : 'tiff';
$rad = isset($_GET["rad"]) ? $_GET["rad"]: "DMX";

$script = "/tmp/nids2gis/". time() .".csh";
$temp = fopen( $script, 'w');

fwrite($temp, "#!/bin/csh
# Dynamically generated script for this NEXRAD request
# NIDS SITE: $rad  FILE: $fp

source /mesonet/nawips/Gemenviron
setenv RAD /mesonet/data/nexrad/

if (! -e iem_n0r.tbl) then
  ln -s /mesonet/TABLES/luts/iem_n0r.tbl
endif

nex2img << EOF > nex2gini.$$.log
 GRDAREA  = $extents[$rad]
 PROJ     = CED
 KXKY     = 600;600
 CPYFIL   =
 GFUNC    = $prod
 RADTIM   = $ts
 RADDUR   = 3
 RADFRQ   =
 STNFIL   = /mesonet/TABLES/nexsites/$rad.stns
 RADMODE  = PC
 RADFIL   = ${rad}_${fp}.gif
 LUTFIL   = $luts[$prod]
 list
 run
                                                                                
 exit
EOF


if (-e ${rad}_${fp}.gif) then
  convert -compress none ${rad}_${fp}.gif ${rad}_${fp}_tmp.tif
  cp /mesonet/data/gis/images/unproj/$rad/n0r_0.tfw ${rad}_${fp}_tmp.tfw
  /usr/bin/gdalwarp -s_srs \"epsg:4326\" -t_srs \"epsg:${epsg}\" ${rad}_${fp}_tmp.tif ${rad}_${fp}.tif
  cp /mesonet/data/gis/meta/${epsg}.prj ${rad}_${fp}.prj
  if (${frmt} == \"jpeg\") then
    /mesonet/local/bin/gdal_translate  -co \"WORLDFILE=ON\" -of JPEG ${rad}_${fp}.tif $$.jpg
    mv $$.wld ${rad}_${fp}.jgw
    convert ${rad}_${fp}.tif ${rad}_${fp}.jpg
    zip ${rad}_${fp}.zip ${rad}_${fp}.jpg ${rad}_${fp}.jgw ${rad}_${fp}.prj
  else
    zip ${rad}_${fp}.zip ${rad}_${fp}.tif ${rad}_${fp}.prj
  endif
  rm -f ${rad}_${fp}.tif ${rad}_${fp}_tmp.tif ${rad}_${fp}_tmp.tfw ${rad}_${fp}.gif ${rad}_${fp}.prj
endif

");

fclose($temp);

chmod($script, 0755);
`$script`;

 header("Content-type: application/octet-stream");
 header("Content-Disposition: attachment; filename=${rad}_${fp}.zip");

 if (file_exists("${rad}_${fp}.zip")){
 	readfile("${rad}_${fp}.zip");
 	unlink("${rad}_${fp}.zip");
 }
//header("Content-type: text/plain");
//readfile($script);

?>
