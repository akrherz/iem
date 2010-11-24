<?php
include("../../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/network.php");
$nt = new NetworkTable("ISUAG");
$ISUAGcities = $nt->table;

$year = isset($_GET["year"]) ? $_GET["year"]: date("Y", time() - 86400 - (7 * 3600) );
$month = isset($_GET["month"]) ? $_GET["month"]: date("m", time() - 86400 - (7 * 3600) );
$day = isset($_GET["day"]) ? $_GET["day"]: date("d", time() - 86400 - (7 * 3600) );
$date = isset($_GET["date"]) ? $_GET["date"]: $year ."-". $month ."-". $day;
$dvar = isset($_GET["dvar"]) ? $_GET["dvar"] : "c90";

$direct = isset($_GET["direct"]) ? $_GET['direct']: "";

$ets = strtotime($date);
$sts = mktime(0,0,0,$month,1,$year);
$sdate = date("d M", $sts);
$edate = date("d M Y", $ets);


include("lib.php");


$myStations = $ISUAGcities;
$height = 480;
$width = 640;

$proj = "proj=tmerc,lat_0=41.5,lon_0=-93.65,x_0=0,y_0=0,k=0.9999";

$map = ms_newMapObj("base.map");
$map->setProjection($proj);
$map->setsize($width,$height);
$map->setextent(-252561, -133255, 300625, 277631);

$counties = $map->getlayerbyname("counties");
$counties->set("status", MS_ON);

$snet = $map->getlayerbyname("snet");
$snet->set("status", MS_ON);
$sclass = $snet->getClass(0);

$iards = $map->getlayerbyname("iards");
$iards->set("status", 1);


$ponly = $map->getlayerbyname("pointonly");
$ponly->set("status", MS_ON);

$img = $map->prepareImage();
$counties->draw($img);
$iards->draw($img);

$c = iemdb("isuag");
$sql = "select station, sum($dvar) as s from daily 
   WHERE extract(month from valid) = $month and
         extract(year from valid) = $year GROUP by station";
$rs =  pg_exec($c, $sql);
for ($i=0; $row = @pg_fetch_array($rs,$i); $i++) {
  $key = $row["station"];
  if ($key == "A133259" or $key == "A130209") continue;

  $val = $row["s"];

  // Red Dot... 
  $pt = ms_newPointObj();
  $pt->setXY($ISUAGcities[$key]['lon'], $ISUAGcities[$key]['lat'], 0);
  $pt->draw($map, $ponly, $img, 0, ' ' );
  $pt->free();

  // Value UL
  $pt = ms_newPointObj();
  $pt->setXY($ISUAGcities[$key]['lon'], $ISUAGcities[$key]['lat'], 0);
  $pt->draw($map, $snet, $img, 0, $val);
  $pt->free();

  // City Name
  $pt = ms_newPointObj();
  $pt->setXY($ISUAGcities[$key]['lon'], $ISUAGcities[$key]['lat'], 0);
  if ($key == "A131909" || $key == "A130209"){
    $pt->draw($map, $snet, $img, 3, $ISUAGcities[$key]['name'] );
  } else {
    $pt->draw($map, $snet, $img, 1, $ISUAGcities[$key]['name'] );
  }
  $pt->free();
}
if ($i == 0)
   plotNoData($map, $img);

$title = Array("c90" => "Rainfall (inches)", "c70" => "Potential Evapotranspiration (in)");
mktitlelocal($map, $img, $height, "      ". $title[$dvar] ." [ $sdate thru ". $edate ." ]");
$map->drawLabelCache($img);

$layer = $map->getLayerByName("logo");
$point = ms_newpointobj();
$point->setXY( 35, 25);
$point->draw($map, $layer, $img, 0, "");
$point->free();

$url = $img->saveWebImage();

if (strlen($direct) > 0) { 
  header("Content-type: image/png");
  $img->saveImage('');
} else {
?>
<img src="<?php echo $url; ?>" border=1>

<?php } ?>
