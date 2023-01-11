<?php
require_once "/usr/lib64/php/modules/mapscript.php";
require_once "../../../../config/settings.inc.php";
require_once "../../../../include/iemmap.php";
require_once "../../../../include/database.inc.php";
require_once "../../../../include/network.php";
$dbconn = iemdb("isuag");
$dvar = isset($_GET["dvar"]) ? $_GET["dvar"] : "rain_in_tot";

$title = Array(
    "rain_in_tot" => "Rainfall (inches)", 
    "dailyet" => "Potential Evapotrans. (in)");
if (!array_key_exists($dvar, $title)) die();

$rs = pg_prepare($dbconn, "SELECT", "select station, sum({$dvar}_qc) as s,
    min(valid) as min_valid, max(valid) as max_valid from sm_daily 
    WHERE extract(month from valid) = $1 and
    extract(year from valid) = $2 GROUP by station");


$nt = new NetworkTable("ISUSM");
$ISUAGcities = $nt->table;

$year = isset($_GET["year"]) ? $_GET["year"]: date("Y", time() - 86400 - (7 * 3600) );
$month = isset($_GET["month"]) ? $_GET["month"]: date("m", time() - 86400 - (7 * 3600) );
$day = isset($_GET["day"]) ? $_GET["day"]: date("d", time() - 86400 - (7 * 3600) );
$date = isset($_GET["date"]) ? $_GET["date"]: $year ."-". $month ."-". $day;

$sts = mktime(0,0,0,$month,1,$year);

$myStations = $ISUAGcities;
$height = 768;
$width = 1024;

$map = new mapObj("../../../../data/gis/base26915.map");
$map->setProjection("init=epsg:26915");
$map->setsize($width,$height);
$map->setextent(175000, 4440000, 775000, 4890000);

$counties = $map->getlayerbyname("counties");
$counties->__set("status", MS_ON);

$snet = $map->getlayerbyname("station_plot");
$snet->__set("status", MS_ON);

$iards = $map->getlayerbyname("iards");
$iards->__set("status", 1);

$bar640t = $map->getlayerbyname("bar640t");
$bar640t->__set("status", MS_ON);

$states = $map->getlayerbyname("states");
$states->__set("status", MS_ON);

$ponly = $map->getlayerbyname("pointonly");
$ponly->__set("status", MS_ON);

$img = $map->prepareImage();
$counties->draw($map, $img);
$states->draw($map, $img);
$iards->draw($map, $img);
$bar640t->draw($map, $img);

$rs = pg_execute($dbconn, "SELECT", Array($month, $year));
$minvalid = null;
$maxvalid = null;
for ($i=0; $row = pg_fetch_assoc($rs); $i++) {
  $key = $row["station"];
  if ($key == "AMFI4" or $key == "AHTI4") continue;

  if (is_null($minvalid) || $row["min_valid"] < $minvalid){
      $minvalid = $row["min_valid"];
  }
  if (is_null($maxvalid) || $row["max_valid"] > $maxvalid){
    $maxvalid = $row["max_valid"];
}
    if ($dvar == "rain_in_tot"){
        $val = round($row["s"],2);
    } else {
        $val = round($row["s"] / 25.4,2);
    }
  $sdate = strtotime( $row["min"] );
  $edate = strtotime( $row["max"] );
  
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
  if ($key == "A131909" || $key == "A130209"){
    $pt->draw($map, $snet, $img, 1, $ISUAGcities[$key]['plot_name'] );
  } else {
    $pt->draw($map, $snet, $img, 1, $ISUAGcities[$key]['plot_name'] );
  }
}
$minvalid = strtotime($minvalid);
$maxvalid = strtotime($maxvalid);
iemmap_title($map, $img, $title[$dvar] ." [ ".
    date("d M", $minvalid) ." thru ". date("d M Y", $maxvalid) ." ]");
$map->drawLabelCache($img);

header("Content-type: image/png");
echo $img->getBytes();
