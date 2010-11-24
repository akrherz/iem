<?php
include("../../../../config/settings.inc.php");
//  mesoplot/plot.php
//  - Replace GEMPAK mesoplots!!!



include("$rootpath/include/mlib.php");
include("$rootpath/include/iemaccess.php");
include("$rootpath/include/iemaccessob.php");
include("$rootpath/include/network.php");

$network = isset($_GET['network']) ? $_GET['network'] : 'KCCI';
$nt = new NetworkTable($network);
$Scities = $nt->table;
$titles = Array("KCCI" => "KCCI SchoolNet8",
 "KELO" => "KELO WeatherNet",
 "KIMT" => "KIMT StormNet");

$iem = new IEMAccess();
$data = $iem->getNetwork($network);



function mktitle($map, $imgObj, $titlet) { 
 
        $layer = $map->getLayerByName("credits");
 
       // point feature with text for location
       $point = ms_newpointobj();
       $point->setXY( 100, 
                     10);

       $point->draw($map, $layer, $imgObj, "credits",
                     $titlet);
}
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


$myStations = Array();
$formStr = "";
$cgiStr = "";
if (! isset($str) ){
  $str = Array();
}

foreach ($Scities as $key => $value) {
    $myStations[$key] = "hi";
}

$var = isset($_GET["var"]) ? $_GET["var"] : "tmpf";

$height = 350;
$width = 450;


$proj = "init=epsg:26915";

$projInObj = ms_newprojectionobj("proj=latlong");
$projOutObj = ms_newprojectionobj($proj);

$varDef = Array("tmpf" => "Current Temperatures",
  "dwpf" => "Current Dew Points",
  "sped" => "Current Wind Speed [MPH]",
  "sknt" => "Current Wind Speed [knts]",
  "barb" => "Current Wind Barbs [knts]",
  "gbarb" => "Today Wind Gust Barbs [knts]",
  "max_sped" => "Today's Wind Gust [MPH]",
  "max_sknt" => "Today's Wind Gust [knts]",
  "feel" => "Currently Feels Like",
  "tmpf_max" => "Today's High Temperature",
  "tmpf_min" => "Today's Low Temperature",
  "pmonth" => "This Month's Precip",
  "pday" => "Today's Precip");

$rnd = Array("tmpf" => 0,
  "dwpf" => 0,
  "sknt" => 0,
  "max_sknt" => 0,
  "feel" => 0,
  "pmonth" => 2,
  "pday" => 2);


$height = 480;
$width = 640;

$map = ms_newMapObj("base.map");
$map->set("width", $width);
$map->set("height", $height);

$map->setprojection($proj);
if (isset($_GET["zoom"]))
  $map->setextent(375000, 4575000, 475000, 4675000);
else
{
  if ($network == "KIMT")
    $map->setextent(420000, 4740000, 600000, 4900000);
  else if ($network == "KELO")
    $map->setextent(-400000, 4600000, 320000, 5200000);
  else
    $map->setextent(300000, 4480000, 550000, 4800000);
}

$counties = $map->getlayerbyname("counties");
$counties->set("status", MS_ON);

$states = $map->getlayerbyname("states");
$states->set("status", MS_ON);

$snet = $map->getlayerbyname("snet");
$snet->set("status", MS_ON);
$sclass = $snet->getClass(0);

$barbs = $map->getlayerbyname("barbs");
$barbs->set("status", MS_ON);
$bclass = $barbs->getClass(0);

$temps = $map->getlayerbyname("temps");
$temps->set("status", MS_ON);
$temps->setprojection("proj=latlong");

$dmx = $map->getlayerbyname("DMX");
$dmx->set("status", MS_ON);

$iards = $map->getlayerbyname("interstates");
$iards->set("status", MS_ON);

$mwradar = $map->getlayerbyname("mwradar");
$mwradar->set("status", MS_ON);

$img = $map->prepareImage();

$counties->draw($img);
$states->draw($img);
$iards->draw($img);
$mwradar->draw($img);
$sclass->label->set("position", "AUTO");
$sclass->label->set("buffer", 2);
$sclass->label->set("force", "true");
$now = time();

foreach($data as $key => $value){

  if ($Scities[$key]["online"] == false) continue;
  $bzz = $value->db;
  if (($now - $bzz["ts"]) < 3600){ 
     $pt = ms_newPointObj();
     $pt->setXY($Scities[$key]["lon"], $Scities[$key]["lat"], 0);
     $rotate =  0 - intval($bzz["drct"]);
     $bclass->label->set("angle", doubleval($rotate));
     $pt->draw($map, $barbs, $img, 0, skntChar($bzz["sknt"]) );
     $pt->free();

     $pt = ms_newPointObj();
     $pt->setXY($Scities[$key]["lon"], $Scities[$key]["lat"], 0);
     $tmpf = intval($bzz['tmpf']);
     $pt->draw($map, $temps, $img, 0, round($bzz['tmpf'], $rnd['tmpf']) );
     $pt->free();

     $pt = ms_newPointObj();
     $pt->setXY($Scities[$key]["lon"], $Scities[$key]["lat"], 0);
     $dwpf = intval($bzz['dwpf']);
     $pt->draw($map, $temps, $img, 1, round($bzz['dwpf'], $rnd['dwpf']) );
     $pt->free();
  }
}

  $ts = strftime("%I %p");

$snet->draw($img);
$temps->draw($img);
//$dmx->draw($img);

//mktitle($map, $img, "     ". $varDef[$var] ." @ ". date("h:i A d M Y") ."                                                    ");
mktitle($map, $img, $titles[$network] ."  Station Plot @ ". date("h:i A d M Y") ."                                                    ");
$map->drawLabelCache($img);

//$pt = ms_newPointObj();
//$pt->setXY(-94, 42, 0);
//$pt->draw($map, $ly2, $img, 0, "");
//$pt->free();

//$layer2->draw($img);
//$ly->draw( $img);

//$img = $map->draw();

//$url = $img->saveWebImage(MS_PNG, 0,0,-1);
header("Content-type: image/png");
$img->saveImage('');
?>
