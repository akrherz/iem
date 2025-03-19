<?php
require_once "../../../../config/settings.inc.php";
require_once "../../../../include/iemmap.php";
require_once "../../../../include/database.inc.php";
require_once "../../../../include/network.php";
require_once "../../../../include/forms.php";
require_once "../../../../include/vendor/mapscript.php";
$nt = new NetworkTable("ISUSM");
$ISUAGcities = $nt->table;

$year = get_int404("year", date("Y", time() - 86400 - (7 * 3600)));
$month = get_int404("month", date("m", time() - 86400 - (7 * 3600)));
$day = get_int404("day", date("d", time() - 86400 - (7 * 3600)));
$date = isset($_GET["date"]) ? xssafe($_GET["date"]) : $year . "-" . $month . "-" . $day;

$ts = strtotime($date);

$myStations = $ISUAGcities;
$height = 480;
$width = 640;

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

$c = iemdb("isuag");
// Figure out when we should start counting
$doy1 = date("j", mktime(0, 0, 0, 9, 1, $year));
$doy2 = date("j", $ts);
$edate = date("Y-m-d", $ts);
if ($month >= 9) {
    $sdate = sprintf("%s-09-01", $year);
    $dateint = "extract(doy from valid) BETWEEN $doy1 and $doy2";
} else {
    $sdate = sprintf("%s-09-01", intval($year) - 1);
    $dateint = "(extract(doy from valid) < $doy1 or extract(doy from valid) > $doy2)";
}

$data = array();
$dbargs = array($sdate, $edate);
$sql = <<<EOM
    select station, min(valid) as v from sm_hourly
    WHERE valid > $1 and tair_c_avg < f2c(29.0) and
    valid < $2 GROUP by station
EOM;
$stname = iem_pg_prepare($c, $sql);
$rs =  pg_execute($c, $stname, $dbargs);

$sql = <<< EOM
    select count(distinct valid) as c from sm_hourly 
    WHERE station = $1 and valid > $2 and valid < $3
    and tair_c_avg >= f2c(32.0) and tair_c_avg <= f2c(45.0)
EOM;
$sub_st1 = iem_pg_prepare($c, $sql);

$sql = <<< EOM
    select count(distinct valid) as c 
    from sm_hourly WHERE station = $1 and tair_c_avg >= f2c(32)
    and tair_c_avg <= f2c(45) 
    and extract(year from valid) >= $2 and 
    extract(year from valid) < extract(year from now()) and
    $dateint
EOM;
$sub_st2 = iem_pg_prepare($c, $sql);

while ($row = pg_fetch_assoc($rs)) {
    $bdate = $sdate;
    $key = $row["station"];

    $data[$key]['name'] = $ISUAGcities[$key]['name'];
    $data[$key]['lon'] = $ISUAGcities[$key]['lon'];
    $data[$key]['lat'] = $ISUAGcities[$key]['lat'];

    $rs2 = pg_execute($c, $sub_st1, array($key, $row["v"], $edate));
    if (pg_num_rows($rs2) == 0) {
        continue;
    }
    $r = pg_fetch_assoc($rs2, 0);
    $val = $r["c"];

    $data[$key]['var'] = $val;

    // Calculate average?
    $syear = 2000;
    if (!is_null($ISUAGcities[$key]["archive_begin"])) {
        $syear = intval($ISUAGcities[$key]["archive_begin"]->format("Y"));
    }

    $rs2 = pg_execute($c, $sub_st2, array($key, $syear));
    if (pg_num_rows($rs2) == 0) continue;
    $r = pg_fetch_assoc($rs2, 0);
    if ((intval(date("Y")) - $syear - 1) == 0) continue;
    $avg = ($r["c"]) / (intval(date("Y")) - $syear - 1);

    $data[$key]['var2'] = round($avg, 0);

    // Red Dot... 
    $pt = new pointObj();
    $pt->setXY($ISUAGcities[$key]['lon'], $ISUAGcities[$key]['lat'], 0);
    $pt->draw($map, $ponly, $img, 0, "");

    // Value UL
    $pt = new pointObj();
    $pt->setXY($ISUAGcities[$key]['lon'], $ISUAGcities[$key]['lat'], 0);
    $pt->draw($map, $snet, $img, 1, $val);

    // City Name
    $pt = new pointObj();
    $pt->setXY($ISUAGcities[$key]['lon'], $ISUAGcities[$key]['lat'], 0);
    if ($key == "A131909" || $key == "A130209") {
        $pt->draw($map, $snet, $img, 0, $ISUAGcities[$key]['name']);
    } else {
        $pt->draw($map, $snet, $img, 0, $ISUAGcities[$key]['name']);
    }
}

iemmap_title(
    $map,
    $img,
    "Standard Chill Units [ $sdate thru " . date("Y-m-d", $ts) . " ]",
    (pg_num_rows($rs) == 0) ? 'No Data Found!' : null
);
$map->drawLabelCache($img);

header("Content-type: image/png");
echo $img->getBytes();
