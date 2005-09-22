<?php

$imgi = 0;

$ts = filemtime("/mesonet/data/gis/images/unproj/USCOMP/n0r_".$imgi.".png") - ($imgi * 300);
echo date("d F Y h:i A T" ,  $ts);

putenv("TZ=GMT");

$ts = filemtime("/mesonet/data/gis/images/unproj/USCOMP/n0r_".$imgi.".png") - ($imgi * 300);
echo date("d F Y h:i A T" ,  $ts);
?>
