<?php
include("../../../../config/settings.inc.php");

$layers =  isset( $_GET['layers']) ? $_GET['layers'] : Array("radar", "labels");
$var    =  isset( $_GET['var']) ? $_GET['var'] : "tmpf";
$network = isset($_GET['network']) ? $_GET['network'] : "";
$st = isset($_GET['st']) ? $_GET['st'] : Array();


function mktitle($map, $imgObj, $titlet) {
  $layer = $map->getLayerByName("credits");

  // point feature with text for location
  $point = ms_newpointobj();
  $point->setXY(5, 12);

  $point->draw($map, $layer, $imgObj, "credits",
    $titlet);
}



include("$rootpath/include/mlib.php");
include("$rootpath/include/iemaccess.php");
include("$rootpath/include/iemaccessob.php");

function skntChar($sknt){
  if ($sknt < 2)  return chr(0);
  if ($sknt < 5)  return chr(227);
  if ($sknt < 10)  return chr(228);
  if ($sknt < 15)  return chr(229);
  if ($sknt < 20)  return chr(230);
  if ($sknt < 25)  return chr(231);
  if ($sknt < 30)  return chr(232);
  if ($sknt < 35)  return chr(233);
  if ($sknt < 40)  return chr(234);
  if ($sknt < 45)  return chr(235);
  if ($sknt < 50)  return chr(236);
  if ($sknt < 55)  return chr(237);
  if ($sknt < 60)  return chr(238);
}

$iem = new IEMAccess();

$sts = Array();

if (isset($st) ){
  foreach ($st as $key => $value) {
    if (strlen($value) > 0 && $value != "ahack") {
      $o = $iem->getSingleSite($value);
      $sts[$value] = $o;      
    }
  }
}


if (strlen($network) > 0){
  $sts = $iem->getNetwork($network);
}

$varDef = Array("tmpf" => "Temperatures",
  "tsf0" => "Pavement Temp #1",
  "tsf1" => "Pavement Temp #2",
  "tsf2" => "Pavement Temp #3",
  "tsf3" => "Pavement Temp #4",
  "dwpf" => "Dew Points",
  "vsby" => "Visibility",
  "sknt" => "Wind [knots]",
  "alti" => "Altimeter",
  "pres" => "Pressure",
  "barb" => "Wind Barbs",
  "max_tmpf" => "Maximum Temperature",
  "max_dwpf" => "Maximum Dew Point",
  "min_tmpf" => "Minimum Temperature",
  "gust" => "Peak Wind Gust [knots]",
  "relh" => "Relative Humidity",
  "phour" => "Hourly Rainfall",
  "pday" => "Today Rainfall",
  "pmonth" => "Rainfall This Month",
  "snow" => "Today Snowfall",
  "snowd" => "Today Snow Depth",
  "snoww" => "Snow Water Equivalent",
  "max_sknt" => "Peak Gust Today [knots]",
  "max_gust" => "Peak Gust Today [knots]",
  "feel" => "Feels Like");

$rnd = Array("alti" => 2, "phour" => 2, "vsby" => 1,"tmpf" => 0,"dwpf"=>0,
  "pday" => 2, "pmonth" => 2, "pres" => 2, "snoww" => 2);

$lats = Array();
$lons = Array();
$height = 350;
$width = 450;

foreach($sts as $key => $value){
  $lats[$key] = $sts[$key]->db["y"];
  $lons[$key] = $sts[$key]->db["x"];
}

$lat0 = min($lats);
$lat1 = max($lats);
$lon0 = min($lons);
$lon1 = max($lons);

$map = ms_newMapObj("$rootpath/data/gis/base4326.map");

$pad = 0.6;
$lpad = 0.6;

//$map->setextent(-83760, -2587, 478797, 433934);
$map->setextent($lon0 - $lpad, $lat0 - $pad, $lon1 + $lpad, $lat1 + $pad);

$namer = $map->getlayerbyname("namerica");
$namer->set("status", 1);
$lakes = $map->getlayerbyname("lakes");
$lakes->set("status", 1);

$GOESBASE="/mesonet/data/gis/images/4326/goes";
$goes_east1V = $map->getlayerbyname("goes_east1V");
$goes_east1V->set("data", "${GOESBASE}/east1V_0.tif");
$goes_east1V->set("status", in_array("goes_east1V", $layers) );

$goes_west1V = $map->getlayerbyname("goes_west1V");
$goes_west1V->set("data", "${GOESBASE}/west1V_0.tif");
$goes_west1V->set("status", in_array("goes_west1V", $layers) );

$goes_west04I4 = $map->getlayerbyname("goes_west04I4");
$goes_west04I4->set("data", "${GOESBASE}/west04I4_0.tif");
$goes_west04I4->set("status",in_array("goes_west04I4", $layers) );

$goes_east04I4 = $map->getlayerbyname("goes_east04I4");
$goes_east04I4->set("data", "${GOESBASE}/east04I4_0.tif");
$goes_east04I4->set("status", in_array("goes_east04I4", $layers));


$currents = $map->getlayerbyname("currents");
$currents->set("status", MS_ON);

$counties = $map->getlayerbyname("uscounties");
$counties->set("status", MS_ON);

$sname = $map->getlayerbyname("sname");
$sname->set("status", MS_ON);

$stlayer = $map->getlayerbyname("states");
$stlayer->set("status", 1);

$radar = $map->getlayerbyname("nexrad_n0r");
$radar->set("status", 1);

$cwa = $map->getlayerbyname("cwas");
$cwa->set("status", 1);

$st_cl = ms_newclassobj($stlayer);
$st_cl->set("status", MS_ON);

$img = $map->prepareImage();
$namer->draw($img);
$lakes->draw($img);

$goes_east1V->draw($img);
$goes_west1V->draw($img);
$goes_east04I4->draw($img);
$goes_west04I4->draw($img);



$ly = ms_newlayerobj($map);
$ly->set("status", MS_ON);
$ly->set("type", MS_LAYER_POINT);
$ly->setProjection("proj=latlong");

$cl = ms_newclassobj($ly);
$cl->set("status", MS_ON);
$cl->set("name", "ccc");
//$cl->set("symbol", 1);
//$cl->set("size", 10);
//$cl->set("color", $green);
//$cl->set("backgroundcolor", $green);

$lbl = $cl->label;
$lbl->set("type", MS_TRUETYPE);
$lbl->set("antialias", MS_OFF);
$lbl->set("font", "arial");
$lbl->set("size", 18);
//$lbl->set("color", $black);
$lbl->set("position", MS_AUTO);
$lbl->set("force", MS_ON);

$ly2 = $map->getLayerByName("pointonly");
$ly2->set("status", MS_ON);
$ly2->setProjection("proj=latlong");

$barbs = $map->getlayerbyname("barbs");
$barbs->set("status", MS_ON);
$bclass = $barbs->getClass(0);

$now = time();
foreach($sts as $key => $value){
  $bzz = $value;
  $sped = $bzz->db["sknt"] * 1.15078;
  $bzz->db["relh"] = relh(f2c($bzz->db["tmpf"]), 
       f2c($bzz->db["dwpf"]) );
  $bzz->db["feel"] = feels_like($bzz->db["tmpf"], 
       $bzz->db["relh"], $sped);
  $val = round(@$bzz->db[$var], @$rnd[$var]);
  $mynetwork = $bzz->db["network"];
  if ( (($now - $bzz->ts) < 3900 || (substr($mynetwork,3,4) == "COOP" || $mynetwork == "IACOCORAHS") && ($now - $bzz->ts) < 86400) && $val > -99 & $val != 99){ 

  if ( in_array('barbs', $layers) ){
    $pt = ms_newPointObj();
    $pt->setXY($bzz->db["x"], $bzz->db["y"], 0);
    $rotate =  0 - intval($bzz->db["drct"]);
    $bclass->label->set("angle", doubleval($rotate));
    $pt->draw($map, $barbs, $img, 0, skntChar($bzz->db["sknt"]) );
    $pt->free();
  }

   if ($var == "barb" && $bzz->db["sknt"] > -1) {
    $pt = ms_newPointObj();
    $pt->setXY($bzz->db["x"], $bzz->db["y"], 0);
    $rotate =  0 - intval($bzz->db["drct"]);
    $bclass->label->set("angle", doubleval($rotate));
    $pt->draw($map, $barbs, $img, 0, skntChar($bzz->db["sknt"]) );
    $pt->free();
                                                                                
    $pt = ms_newPointObj();
    $pt->setXY($bzz->db["x"], $bzz->db["y"], 0);
    $pt->draw($map, $currents, $img, 0, round($bzz->db['sknt'], @$rnd['sknt']) );
    $pt->free();
   } else if ($var != "barb" && $val > -99){
     $pt = ms_newPointObj();
     $pt->setXY($bzz->db["x"], $bzz->db["y"], 0);
     $pt->draw($map, $currents, $img, 0, $val );
     $pt->free();
   }
   if (in_array('labels', $layers)) {
    if (strlen($network) == 0){
     $pt = ms_newPointObj();
     $pt->setXY($bzz->db["x"], $bzz->db["y"], 0);
     $pt->draw($map, $sname, $img, 0, $bzz->db["sname"] );
     $pt->free();
    } else {
     $pt = ms_newPointObj();
     $pt->setXY($bzz->db["x"], $bzz->db["y"], 0);
     $pt->draw($map, $sname, $img, 0, $key );
     $pt->free();
    }
   }
  }
}

$ts = strftime("%d %b @ %I:%M %p");



if (in_array('county', $layers))
  $counties->draw($img);
$stlayer->draw( $img);
if (in_array('radar', $layers))
  $radar->draw($img);
if (in_array('cwa', $layers))
  $cwa->draw($img);

$title = $ts ." ". $network ." ". $varDef[$var] ;
if (in_array('barbs', $layers)){ $title .= " and Wind Barbs"; }
mktitle($map, $img, $title);

$map->drawLabelCache($img);

header("Content-type: image/png");
$img->saveImage('');
?>
