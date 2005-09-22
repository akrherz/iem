<?php

dl("php_mapscript.so");

$projInObj = ms_newprojectionobj("proj=lcc,lat_1=20,lat_2=60,lat_0=40,lon_0=-96,x_0=0,y_0=0");
$projOutObj = ms_newprojectionobj("init=epsg:4269");

$point = ms_newpointobj();
$point->setXY(2000000, 1400000);
$lp0 = $point->project($projInObj, $projOutObj);

print_r($lp0);

?>
