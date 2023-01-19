<?php
require_once "/usr/lib64/php/modules/mapscript.php";

require_once "../../../../config/settings.inc.php";
require_once "../../../../include/iemmap.php";
require_once "../../../../include/forms.php";

$var = isset($_GET["var"]) ? $_GET["var"] : "gdd50";
$year = get_int404("year", date("Y"));
$smonth = get_int404("smonth", 5);
$emonth = get_int404("emonth", 9);
$sday = get_int404("sday", 1);
$eday = get_int404("eday", 30);
$imgsz = isset($_GET["imgsz"]) ? $_GET["imgsz"] : "640x480";
$ar = explode("x", $imgsz);
$width = $ar[0];
$height = $ar[1];

$gddbase = 50;
$datavar = $var;
if (substr($var, 0, 3) == "gdd") {
    $gddbase = intval(str_replace("gdd", "", $var));
    $datavar = "gdd";
}
if (substr($var, 0, 4) == "sgdd") {
    $gddbase = intval(str_replace("sgdd", "", $var));
    $datavar = "sgdd";
}

$wsuri = sprintf(
    "/api/1/isusm/daily.geojson?sdate=%s-%s-%s&edate=%s-%s-%s&" .
        "gddbase=%s&gddceil=%s",
    $year,
    $smonth,
    $sday,
    $year,
    $emonth,
    $eday,
    $gddbase,
    86
);

$varDef = array(
    "gdd32" => "Growing Degree Days (base=32)",
    "gdd41" => "Growing Degree Days (base=41)",
    "gdd46" => "Growing Degree Days (base=46)",
    "gdd48" => "Growing Degree Days (base=48)",
    "gdd50" => "Growing Degree Days (base=50)",
    "gdd51" => "Growing Degree Days (base=51)",
    "gdd52" => "Growing Degree Days (base=52)",
    "et" => "Potential Evapotranspiration (inch)",
    "precip" => "Precipitation (inch)",
    "srad" => "Solar Radiation (langleys)",
    "sgdd50" => "Soil Growing Degree Days (base=50)",
    "sgdd52" => "Soil Growing Degree Days (base=52)",
    "sdd86" => "Stress Degree Days (base=86)"
);

$rnd = array(
    "gdd" => 0,
    "et" => 2, "c11" => 2,
    "precip" => 2,
    "srad" => 0,
    "sgdd" => 0
);

$proj = "init=epsg:26915";

$map = new mapObj("../../../../data/gis/base26915.map");
$map->setsize($width, $height);
$map->setProjection($proj);

$map->setextent(175000, 4440000, 775000, 4890000);

$counties = $map->getlayerbyname("counties");
$counties->__set("status", MS_ON);

$snet = $map->getlayerbyname("station_plot");
$snet->__set("status", MS_ON);

$iards = $map->getlayerbyname("iards");
$iards->__set("status", MS_ON);

$bar640t = $map->getlayerbyname("bar640t");
$bar640t->__set("status", MS_ON);

$ponly = $map->getlayerbyname("pointonly");
$ponly->__set("status", MS_ON);

$states = $map->getlayerbyname("states");
$states->__set("status", MS_ON);

$img = $map->prepareImage();
$counties->draw($map, $img);
$states->draw($map, $img);
$iards->draw($map, $img);
$bar640t->draw($map, $img);

$sdate = new DateTime("{$year}-{$smonth}-{$sday}");
$edate = new DateTime("{$year}-{$emonth}-{$eday}");
$sstr_txt = $sdate->format("M j");
$estr_txt = $edate->format("M j");

$jdata = file_get_contents("http://iem.local" . $wsuri);
$jobj = json_decode($jdata, $assoc = TRUE);

foreach ($jobj["features"] as $bogus => $value) {
    $props = $value["properties"];
    $value = $props[$datavar];
    if (is_null($value)) {
        continue;
    }
    $sid = $props["station"];
    $lon = $props["lon"];
    $lat = $props["lat"];
    if ($datavar == "et" && $sid == "GVNI4") {
        continue;
    }
    if ($sid == "DONI4") {
        $lat -= 0.2;
    } elseif ($sid == "AHTI4") {
        $lat += 0.2;
        $lon -= 0.2;
    } elseif ($sid == "AKCI4") {
        $lat -= 0.2;
        $lon += 0.2;
    } elseif ($sid == "AMFI4") {
        continue;
    } elseif ($sid == "BOOI4") {
        $lon -= 0.2;
    } elseif ($sid == "FRUI4") {
        $lat -= 0.05;
    }

    // Red Dot... 
    $pt = new pointObj();
    $pt->setXY($lon, $lat, 0);
    $pt->draw($map, $ponly, $img, 0, "");

    // Value UL
    $pt = new pointObj();
    $pt->setXY($lon, $lat, 0);
    $pt->draw($map, $snet, $img, 1, round($value, $rnd[$datavar]));

    // Climate
    if (substr($var, 0, 3) == "gdd" || $var == "precip") {
        $pt = new pointObj();
        $pt->setXY($lon, $lat, 0);
        $pt->draw($map, $snet, $img, 2, "(" . round($value - $props["climo_" . $datavar], $rnd[$datavar]) . ")");
    }

    // City Name
    $pt = new pointObj();
    $pt->setXY($lon, $lat, 0);
    $ar = explode("-", $props['name']);
    $pt->draw($map, $snet, $img, 0, $ar[0]);
}

iemmap_title(
    $map,
    $img,
    $year . " " . $varDef[$var],
    "(" . $sstr_txt . " - " . $estr_txt . ") [some stations moved for legibility]"
);
$map->drawLabelCache($img);

header("Content-type: image/png");
echo $img->getBytes();
