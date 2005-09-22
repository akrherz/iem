<?php

dl("php_mapscript.so");
include('../../../include/mlib.php');
include('../../../include/currentOb.php');
include('../../../include/allLoc.php');


#$myStations = Array();
#$handle = opendir("/mesonet/data/current/asos/");
#while (false !== ($file = readdir($handle))) { 
#  if ($file != "." && $file != "..") {
#    array_push($myStations, substr($file,0,3) );
#  } // End of if
#} // End of while
#closedir($handle);

$myStations2 = Array();
$handle = opendir("/mesonet/data/current/awos/");
while (false !== ($file = readdir($handle))) { 
  if ($file != "." && $file != "..") {
    array_push($myStations2, substr($file,0,3) );
  } // End of if
} // End of while
closedir($handle);

$myStations3 = Array();
$handle = opendir("/mesonet/data/current/rwis/");
while (false !== ($file = readdir($handle))) { 
  if ($file != "." && $file != "..") {
    array_push($myStations3, substr($file,0,4) );
  } // End of if
} // End of while
closedir($handle);

$myStations4 = Array();
$handle = opendir("/mesonet/data/current/IAshef/");
while (false !== ($file = readdir($handle))) { 
  if ($file != "." && $file != "..") {
    array_push($myStations4, substr($file,0,5) );
  } // End of if
} // End of while
closedir($handle);

$myStations5 = Array(
  "SHAG" => Array("lat"=> 42.43 , "lon" => -95.76),
  "AMES" => Array("lat"=> 42.00 , "lon" => -93.72) );

$myStations6 = array(
"A130209" => array("city" => "AMES", "lat" => "42.03", "lon" => "-93.80"),
"A131069" => array("city" => "CALMAR", "lat" => "43.16", "lon" => "-91.87"),
"A131299" => array("city" => "CASTANA", "lat" => "42.06",  "lon" => "-95.82"),
"A131329" => array("city" => "CEDAR RAPIDS", "lat" => "41.90", "lon" =>  "-91.50"),
"A131559" => array("city" => "CHARITON", "lat" => "41.00", "lon" => "-93.32"),
"A131909" => array("city" => "CRAWFORDSVILLE", "lat" => "41.20", "lon" => "-91.50"),
"A135879" => array("city" => "NASHUA", "lat" => "42.75", "lon" => "-92.50"),
"A138019" => array("city" => "SUTHERLAND", "lat" => "42.96", "lon" =>  "-95.50"),
"A134759" => array("city" => "LEWIS", "lat" => "41.40", "lon" => "-95.00"),
"A136949" => array("city" => "RHODES", "lat" => "42.00",  "lon" => "-93.25"),
"A134309" => array("city" => "KANAWHA", "lat" => "42.94", "lon" => "-93.90"),
"A135849" => array("city" => "MUSCATINE", "lat" => "41.22", "lon" => "-91.06")
);


$myStations7 = Array();
$handle = opendir("/mesonet/data/current/coop/");
while (false !== ($file = readdir($handle))) { 
  if ($file != "." && $file != "..") {
    array_push($myStations7, substr($file,0,5) );
  } // End of if
} // End of while
closedir($handle);

$myStations8 = Array();
$handle = opendir("/mesonet/data/current/kcci/");
while (false !== ($file = readdir($handle))) { 
  if ($file != "." && $file != "..") {
    array_push($myStations8, substr($file,0,5) );
  } // End of if
} // End of while
closedir($handle);

$myStations9 = Array();
$handle = opendir("/tmp/coop/");
while (false !== ($file = readdir($handle))) { 
  if ($file != "." && $file != "..") {
    array_push($myStations9, substr($file,0,5) );
  } // End of if
} // End of while
closedir($handle);

$myStations5 = $myStations5;

#$lats = Array();
#$lons = Array();
$height = 480;
$width = 640;

#foreach($myStations as $key => $value){
#  $lats[$value] = $cities[$value]["lat"];
#  $lons[$value] = $cities[$value]["lon"];
#}

#$lat0 = min($lats);
#$lat1 = max($lats);
#$lon0 = min($lons);
#$lon1 = max($lons);
#echo  "$lat0 $lat1 $lon0 $lon1";
$lat0 = 40.62;
$lat1 = 43.4; 
$lon0 = -96.38; 
$lon1 = -90.33;

$map = ms_newMapObj("network.map");

$pad = 1;
$lpad = 0.4;

//$map->setextent(-83760, -2587, 478797, 433934);
$map->setextent($lon0 - $lpad, $lat0 - $pad, $lon1 + $lpad, $lat1 + $pad);

$green = $map->addColor(0, 255, 0);
$blue = $map->addColor(0, 0, 255);
$black = $map->addColor(0, 0, 0);
$white = $map->addColor(255, 255, 255);

$counties = $map->getlayerbyname("counties");
$counties->set("status", MS_ON);

$stlayer = $map->getlayerbyname("states");
$stlayer->set("status", 1);

$dot = $map->getlayerbyname("dot");
$dot->set("status", MS_ON);

$st_cl = ms_newclassobj($stlayer);
$st_cl->set("outlinecolor", $green);
$st_cl->set("status", MS_ON);

$img = $map->prepareImage();

$stlayer->draw( $img);
$counties->draw($img);

/**
foreach($myStations as $key => $value){
   $pt = ms_newPointObj();
   $pt->setXY($cities[$value]["lon"], $cities[$value]["lat"], 0);
   $pt->draw($map, $dot, $img, 0, "" );
   $pt->free();
}

foreach($myStations2 as $key => $value){
   $pt = ms_newPointObj();
   $pt->setXY($cities[$value]["lon"], $cities[$value]["lat"], 0);
   $pt->draw($map, $dot, $img, 1, "" );
   $pt->free();
}
foreach($myStations3 as $key => $value){
   $pt = ms_newPointObj();
   $pt->setXY($cities[$value]["lon"], $cities[$value]["lat"], 0);
   $pt->draw($map, $dot, $img, 2, "" );
   $pt->free();
}
foreach($myStations4 as $key => $value){
   $pt = ms_newPointObj();
   $pt->setXY($cities[$value]["lon"], $cities[$value]["lat"], 0);
   $pt->draw($map, $dot, $img, 3, "" );
   $pt->free();
}
*/
foreach($myStations5 as $key => $value){
   $pt = ms_newPointObj();
   $pt->setXY($myStations5[$key]["lon"], $myStations5[$key]["lat"], 0);
   $pt->draw($map, $dot, $img, 0, "" );
   $pt->free();
}
/**
foreach($myStations6 as $key => $value){
   $pt = ms_newPointObj();
   $pt->setXY($myStations6[$key]["lon"], $myStations6[$key]["lat"], 0);
   $pt->draw($map, $dot, $img, 5, "" );
   $pt->free();
}
foreach($myStations7 as $key => $value){
   $pt = ms_newPointObj();
   $pt->setXY($cities[$value]["lon"], $cities[$value]["lat"], 0);
   $pt->draw($map, $dot, $img, 6, "" );
   $pt->free();
}
foreach($myStations8 as $key => $value){
   $pt = ms_newPointObj();
   $pt->setXY($cities[$value]["lon"], $cities[$value]["lat"], 0);
   $pt->draw($map, $dot, $img, 7, "" );
   $pt->free();
}
foreach($myStations9 as $key => $value){
   $pt = ms_newPointObj();
   $pt->setXY($cities[$value]["lon"], $cities[$value]["lat"], 0);
   $pt->draw($map, $dot, $img, 8, "" );
   $pt->free();
}
 */

#  $ts = strftime("%d %b %I%p");

//$stlayer->draw( $img);
///$counties->draw($img);
//$dot->draw($img);


//$pt = ms_newPointObj();
//$pt->setXY(-94, 42, 0);
//$pt->draw($map, $ly2, $img, 0, "");
//$pt->free();

//$layer2->draw($img);
//$ly->draw( $img);

//$img = $map->draw();
$map->drawLabelCache($img);

$url = $img->saveWebImage(MS_PNG, 0,0,-1);

#$im = @imagecreatefrompng("/mesonet/www/html/". $url );

#$Font = "arialblk.ttf";

// Figure out how big to draw the bottom box!
# $size = imagettfbbox(18, 0, $Font, $title);
# $dx = abs($size[2] - $size[0]);
# $dy = abs($size[5]);
# $ypad = 10;
# $xpad = 30;
# imagefilledrectangle ( $im, $width - $dx - $xpad, $height - $ypad - $dy, 
#   $width, $height - $ypad, $blue);
#
# ImageTTFText($im, 18, 0, $width - $dx - $xpad + 5, $height - $ypad, 
#   $white, $Font, $title );
#
#ImagePng($im , "/mesonet/www/html/". $url );
#ImageDestroy($im);


echo "<img src=\"$url\">";


?>
