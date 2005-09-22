<?php

function mktitle($map, $imgObj, $titlet) {
  $layer = $map->getLayerByName("credits");

  // point feature with text for location
  $point = ms_newpointobj();
  $point->setXY(5, 12);

  $point->draw($map, $layer, $imgObj, "credits",
    $titlet);
}


dl("php_mapscript.so");
include('../../../include/mlib.php');
include('../../../include/currentOb.php');
include('../../../include/allLoc.php');
include('../../../include/iemaccess.php');
include('../../../include/iemaccessob.php');


$myStations = Array();
if (isset($st) ){
foreach ($st as $key => $value) {
  if (strlen($value) > 0 && $value != "ahack") {
    array_push( $myStations, $value);
  }
}
}

if ($network == "AWOS"){
  include("../../../include/awosLoc.php");
  $myStations = array_keys($Wcities);
}
if ($network == "RWIS"){
  include("../../../include/rwisLoc.php");
  $myStations = array_keys($Rcities);
}
if ($network == "ASOS"){
  include("../../../include/asosLoc.php");
  $myStations = array_keys($Acities);
}
if ($network == "KCCI"){
  include("../../../include/kcciLoc.php");
  $myStations = array_keys($Scities);
  $cities = $Scities;
}

if (strlen($var) == 0){
  $var = "tmpf";
}

$varDef = Array("tmpf" => "Temperatures",
  "dwpf" => "Dew Points",
  "vsby" => "Visibility",
  "sknt" => "Wind [knots]",
  "alti" => "Altimeter",
  "min_tmpf" => "Minimum Temperature",
  "gust" => "Peak Wind Gust [knots]",
  "relh" => "Relative Humidity",
  "phour" => "Hourly Rainfall",
  "pday" => "Today Rainfall",
  "max_sknt" => "Peak Gust Today [knots]",
  "max_gust" => "Peak Gust Today [knots]",
  "feel" => "Feel's Like");

$rnd = Array("alti" => 2, "phour" => 2,
  "pday" => 2);

$lats = Array();
$lons = Array();
$height = 350;
$width = 450;

foreach($myStations as $key => $value){
  $lats[$value] = $cities[$value]["lat"];
  $lons[$value] = $cities[$value]["lon"];
}

$lat0 = min($lats);
$lat1 = max($lats);
$lon0 = min($lons);
$lon1 = max($lons);


$map = ms_newMapObj("base.map");

$pad = 0.6;
$lpad = 0.6;

//$map->setextent(-83760, -2587, 478797, 433934);
$map->setextent($lon0 - $lpad, $lat0 - $pad, $lon1 + $lpad, $lat1 + $pad);

$green = $map->addColor(0, 255, 0);
$blue = $map->addColor(0, 0, 255);
$black = $map->addColor(0, 0, 0);
$white = $map->addColor(255, 255, 255);

$currents = $map->getlayerbyname("currents");
$currents->set("status", MS_ON);

$counties = $map->getlayerbyname("counties");
$counties->set("status", MS_ON);

$sname = $map->getlayerbyname("sname");
$sname->set("status", MS_ON);

$stlayer = $map->getlayerbyname("states");
$stlayer->set("status", 1);

$st_cl = ms_newclassobj($stlayer);
$st_cl->set("outlinecolor", $green);
$st_cl->set("status", MS_ON);

$img = $map->prepareImage();

$ly = ms_newlayerobj($map);
$ly->set("status", MS_ON);
$ly->set("type", MS_LAYER_POINT);
$ly->setProjection("proj=latlong");

$cl = ms_newclassobj($ly);
$cl->set("status", MS_ON);
$cl->set("name", "ccc");
$cl->set("symbol", 1);
$cl->set("size", 10);
$cl->set("color", $green);
$cl->set("backgroundcolor", $green);

$lbl = $cl->label;
$lbl->set("type", MS_TRUETYPE);
$lbl->set("antialias", MS_OFF);
$lbl->set("font", "arial");
$lbl->set("size", 18);
$lbl->set("color", $black);
$lbl->set("position", MS_AUTO);
$lbl->set("force", MS_ON);

$ly2 = $map->getLayerByName("pointonly");
$ly2->set("status", MS_ON);
$ly2->setProjection("proj=latlong");

$now = time();
$iem = new IEMAccess();
foreach($myStations as $key => $value){
  //$bzz = currentOb($value);
  $bzz = $iem->getSingleSiteYest($value);
  if (($now - $bzz->ts) < 3900){ 
   $pt = ms_newPointObj();
   $pt->setXY($cities[$value]["lon"], $cities[$value]["lat"], 0);
   $pt->draw($map, $currents, $img, 0, round($bzz->db[$var], $rnd[$var]) );
   $pt->free();

   if (strlen($network) == 0){
    $pt = ms_newPointObj();
    $pt->setXY($cities[$value]["lon"], $cities[$value]["lat"], 0);
    $pt->draw($map, $sname, $img, 0, $cities[$value]["city"] );
    $pt->free();
   } else {
    $pt = ms_newPointObj();
    $pt->setXY($cities[$value]["lon"], $cities[$value]["lat"], 0);
    $pt->draw($map, $sname, $img, 0, $value );
    $pt->free();
   }
  }
}

  $ts = "2003 Nov 12";

$stlayer->draw( $img);
$counties->draw($img);
$currents->draw($img);
$sname->draw($img);

mktitle($map, $img, $ts ." ". $network ." ". $varDef[$var] );

$map->drawLabelCache($img);

$url = $img->saveWebImage(MS_PNG, 0,0,-1);

echo "<img src=\"$url\">";


?>


