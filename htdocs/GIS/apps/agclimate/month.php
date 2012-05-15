<?php
include("../../../../config/settings.inc.php");
include_once "$rootpath/include/iemmap.php";
include("$rootpath/include/database.inc.php");
$dbconn = iemdb("isuag");
$dvar = isset($_GET["dvar"]) ? $_GET["dvar"] : "c90";
$rs = pg_prepare($dbconn, "SELECT", "select station, sum($dvar) as s from daily 
   WHERE extract(month from valid) = $1 and
         extract(year from valid) = $2 GROUP by station");


include("$rootpath/include/network.php");
$nt = new NetworkTable("ISUAG");
$ISUAGcities = $nt->table;

$year = isset($_GET["year"]) ? $_GET["year"]: date("Y", time() - 86400 - (7 * 3600) );
$month = isset($_GET["month"]) ? $_GET["month"]: date("m", time() - 86400 - (7 * 3600) );
$day = isset($_GET["day"]) ? $_GET["day"]: date("d", time() - 86400 - (7 * 3600) );
$date = isset($_GET["date"]) ? $_GET["date"]: $year ."-". $month ."-". $day;

$direct = isset($_GET["direct"]) ? $_GET['direct']: "";
$ets = strtotime($date);
$sts = mktime(0,0,0,$month,1,$year);
$sdate = date("d M", $sts);
$edate = date("d M Y", $ets);

$myStations = $ISUAGcities;
$height = 480;
$width = 640;

$map = ms_newMapObj("$rootpath/data/gis/base26915.map");
$map->setProjection("init=epsg:26915");
$map->setsize($width,$height);
$map->setextent(175000, 4440000, 775000, 4890000);

$counties = $map->getlayerbyname("counties");
$counties->set("status", MS_ON);

$snet = $map->getlayerbyname("station_plot");
$snet->set("status", MS_ON);

$iards = $map->getlayerbyname("iards");
$iards->set("status", 1);

$bar640t = $map->getlayerbyname("bar640t");
$bar640t->set("status", MS_ON);

$states = $map->getlayerbyname("states");
$states->set("status", MS_ON);

$ponly = $map->getlayerbyname("pointonly");
$ponly->set("status", MS_ON);

$img = $map->prepareImage();
$counties->draw($img);
$states->draw($img);
$iards->draw($img);
$bar640t->draw($img);

$rs = pg_execute($dbconn, "SELECT", Array($month, $year));

for ($i=0; $row = @pg_fetch_assoc($rs,$i); $i++) {
  $key = $row["station"];
  if ($key == "A133259" or $key == "A130209") continue;

  $val = $row["s"];

  // Red Dot... 
  $pt = ms_newPointObj();
  $pt->setXY($ISUAGcities[$key]['lon'], $ISUAGcities[$key]['lat'], 0);
  $pt->draw($map, $ponly, $img, 0, ' ' );

  // Value UL
  $pt = ms_newPointObj();
  $pt->setXY($ISUAGcities[$key]['lon'], $ISUAGcities[$key]['lat'], 0);
  $pt->draw($map, $snet, $img, 0, $val);

  // City Name
  $pt = ms_newPointObj();
  $pt->setXY($ISUAGcities[$key]['lon'], $ISUAGcities[$key]['lat'], 0);
  if ($key == "A131909" || $key == "A130209"){
    $pt->draw($map, $snet, $img, 1, $ISUAGcities[$key]['name'] );
  } else {
    $pt->draw($map, $snet, $img, 1, $ISUAGcities[$key]['name'] );
  }
}
if ($i == 0)
   plotNoData($map, $img);

$title = Array("c90" => "Rainfall (inches)", "c70" => "Potential Evapotrans. (in)");

iemmap_title($map, $img, $title[$dvar] ." [ $sdate thru ". $edate ." ]");
$map->drawLabelCache($img);

$url = $img->saveWebImage();

if (strlen($direct) > 0) { 
  header("Content-type: image/png");
  $img->saveImage('');
} else {
?>
<img src="<?php echo $url; ?>" border=1>

<?php } ?>
