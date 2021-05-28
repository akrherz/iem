<?php
require_once "../../../../config/settings.inc.php";
require_once "../../../../include/iemmap.php";

$var = isset($_GET["var"]) ? $_GET["var"] : "gdd50";
$year = isset($_GET["year"]) ? $_GET["year"] : date("Y");
$smonth = isset($_GET["smonth"]) ? $_GET["smonth"]:  5;
$emonth = isset($_GET["emonth"]) ? $_GET["emonth"]: 10;
$sday = isset($_GET["sday"]) ? $_GET["sday"]: 1;
$eday = isset($_GET["eday"]) ? $_GET["eday"]: 1;
$imgsz = isset($_GET["imgsz"]) ? $_GET["imgsz"] : "640x480";
$ar = explode("x", $imgsz);
$width = $ar[0];
$height = $ar[1];

$gddbase = 50;
$datavar = $var;
if (substr($var, 0, 3) == "gdd"){
    $gddbase = intval(str_replace("gdd", "", $var));
    $datavar = "gdd";
}
if (substr($var, 0, 4) == "sgdd"){
    $gddbase = intval(str_replace("sgdd", "", $var));
    $datavar = "sgdd";
}

$wsuri = sprintf(
    "/api/1/isusm/daily.geojson?sdate=%s-%s-%s&edate=%s-%s-%s&".
    "gddbase=%s&gddceil=%s",
    $year, $smonth, $sday, $year, $emonth, $eday, $gddbase, 86
);

$varDef = Array(
  "gdd32" => "Growing Degree Days (base=32)",
  "gdd41" => "Growing Degree Days (base=41)",
  "gdd46" => "Growing Degree Days (base=46)",
  "gdd48" => "Growing Degree Days (base=48)",
  "gdd50" => "Growing Degree Days (base=50)",
  "gdd51" => "Growing Degree Days (base=51)",
  "gdd52" => "Growing Degree Days (base=52)",
  "et" => "Potential Evapotranspiration",
  "precip" => "Precipitation",
  "srad" => "Solar Radiation (langleys)",
  "sgdd50" => "Soil Growing Degree Days (base=50)",
  "sgdd52" => "Soil Growing Degree Days (base=52)",
  "sdd86" => "Stress Degree Days (base=86)"
);


$rnd = Array(
  "gdd" => 0,
  "et" => 2, "c11" => 2,
  "precip" => 2,
  "srad" => 0,
  "sgdd" => 0);


$height = $height;
$width = $width;

$proj = "init=epsg:26915";

$map = ms_newMapObj("../../../../data/gis/base26915.map");
$map->setsize($width,$height);
$map->setProjection($proj);

$map->setextent(175000, 4440000, 775000, 4890000);

$counties = $map->getlayerbyname("counties");
$counties->set("status", MS_ON);

$snet = $map->getlayerbyname("station_plot");
$snet->set("status", MS_ON);

$iards = $map->getlayerbyname("iards");
$iards->set("status", MS_ON);

$bar640t = $map->getlayerbyname("bar640t");
$bar640t->set("status", MS_ON);

$ponly = $map->getlayerbyname("pointonly");
$ponly->set("status", MS_ON);

$states = $map->getlayerbyname("states");
$states->set("status", MS_ON);

$img = $map->prepareImage();
$counties->draw($img);
$states->draw($img);
$iards->draw($img);
$bar640t->draw($img);

$sdate = mktime(0, 0, 0, $smonth, $sday, $year);
$edate = mktime(0, 0, 0, $emonth, $eday, $year);
$sstr_txt = strftime("%b %d", $sdate);
$estr_txt = strftime("%b %d", $edate);

$jdata = file_get_contents("http://iem.local". $wsuri);
$jobj = json_decode($jdata, $assoc=TRUE);

foreach($jobj["features"] as $bogus => $value) {
    $props = $value["properties"];
    $value = $props[$datavar];
    if ($value === null){
        continue;
    }

    // Red Dot... 
    $pt = ms_newPointObj();
    $pt->setXY($props['lon'], $props['lat'], 0);
    $pt->draw($map, $ponly, $img, 0);

    // Value UL
    $pt = ms_newPointObj();
    $pt->setXY($props['lon'], $props['lat'], 0);
    $pt->draw($map, $snet, $img, 1, round($value, $rnd[$datavar]) );

    // Climate
    if (substr($var, 0, 3) == "gdd" || $var == "precip")
    {
        $pt = ms_newPointObj();
        $pt->setXY($props['lon'], $props['lat'], 0);
        $pt->draw($map, $snet, $img, 2, "(". round($value - $props["climo_". $datavar], $rnd[$datavar]) .")");

    }

    // City Name
    $pt = ms_newPointObj();
    $pt->setXY($props['lon'], $props['lat'], 0);
    $ar = explode("-", $props['name']);
    $pt->draw($map, $snet, $img, 0, $ar[0] );
}

iemmap_title($map, $img, $year." ". $varDef[$var] , 
	"(". $sstr_txt ." - ". $estr_txt .")");
$map->drawLabelCache($img);

header("Content-type: image/png");
$img->saveImage('');

?>
