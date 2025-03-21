<?php
require_once "../../../../config/settings.inc.php";
require_once "../../../../include/iemmap.php";
require_once "../../../../include/database.inc.php";
require_once "../../../../include/network.php";
require_once "../../../../include/forms.php";
require_once "../../../../include/vendor/mapscript.php";

$dbconn = iemdb("isuag");
$dvar = isset($_GET["dvar"]) ? xssafe($_GET["dvar"]) : "rain_in_tot";

$title = array(
    "rain_in_tot" => "Rainfall (inches)",
    "dailyet" => "Potential Evapotrans. (in)"
);
if (!array_key_exists($dvar, $title)) die();

$stname = iem_pg_prepare($dbconn, "select station, sum({$dvar}_qc) as s,
    min(valid) as min_valid, max(valid) as max_valid from sm_daily 
    WHERE extract(month from valid) = $1 and
    extract(year from valid) = $2 GROUP by station");

$nt = new NetworkTable("ISUSM");
$ISUAGcities = $nt->table;

$year = get_int404("year", date("Y", time() - 86400 - (7 * 3600)));
$month = get_int404("month", date("m", time() - 86400 - (7 * 3600)));
$day = get_int404("day", date("d", time() - 86400 - (7 * 3600)));

$sts = mktime(0, 0, 0, $month, 1, $year);

$myStations = $ISUAGcities;
$height = 768;
$width = 1024;

$map = new mapObj("../../../../data/gis/base26915.map");
$map->setProjection("init=epsg:26915");
$map->setsize($width, $height);
$map->setextent(175000, 4440000, 775000, 4890000);

$counties = $map->getLayerByName("counties");
$counties->__set("status", MS_ON);

$snet = $map->getLayerByName("station_plot");
$snet->__set("status", MS_ON);

$iards = $map->getLayerByName("iards");
$iards->__set("status", 1);

$bar640t = $map->getLayerByName("bar640t");
$bar640t->__set("status", MS_ON);

$states = $map->getLayerByName("states");
$states->__set("status", MS_ON);

$ponly = $map->getLayerByName("pointonly");
$ponly->__set("status", MS_ON);

$img = $map->prepareImage();
$counties->draw($map, $img);
$states->draw($map, $img);
$iards->draw($map, $img);
$bar640t->draw($map, $img);

$rs = pg_execute($dbconn, $stname, array($month, $year));
$minvalid = null;
$maxvalid = null;
while ($row = pg_fetch_assoc($rs)) {
    $key = $row["station"];
    if ($key == "AMFI4" or $key == "AHTI4") continue;
    $minv = strtotime($row["min_valid"]);
    $maxv = strtotime($row["max_valid"]);

    if (is_null($minvalid) || $minv < $minvalid) {
        $minvalid = $minv;
    }
    if (is_null($maxvalid) || $maxv > $maxvalid) {
        $maxvalid = $maxv;
    }
    if ($dvar == "rain_in_tot") {
        $val = round($row["s"], 2);
    } else {
        $val = round($row["s"] / 25.4, 2);
    }

    // Red Dot... 
    $pt = new pointObj();
    $pt->setXY($ISUAGcities[$key]['lon'], $ISUAGcities[$key]['lat'], 0);
    $pt->draw($map, $ponly, $img, 0, "");

    // Value UL
    $pt = new pointObj();
    $pt->setXY($ISUAGcities[$key]['lon'], $ISUAGcities[$key]['lat'], 0);
    $pt->draw($map, $snet, $img, 0, $val);

    // City Name
    $pt = new pointObj();
    $pt->setXY($ISUAGcities[$key]['lon'], $ISUAGcities[$key]['lat'], 0);
    if ($key == "A131909" || $key == "A130209") {
        $pt->draw($map, $snet, $img, 1, $ISUAGcities[$key]['plot_name']);
    } else {
        $pt->draw($map, $snet, $img, 1, $ISUAGcities[$key]['plot_name']);
    }
}
if (!is_null($minvalid)) {
    $minvalid = date("Y-m-d", $minvalid);
    $maxvalid = date("Y-m-d", $maxvalid);
    iemmap_title($map, $img, $title[$dvar] . " [ " .
        $minvalid . " thru " . $maxvalid . " ]");
}
$map->drawLabelCache($img);

header("Content-type: image/png");
echo $img->getBytes();
