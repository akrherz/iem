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


$direct = isset($_GET["direct"]) ? $_GET['direct']: "";

$ts = strtotime($date);

dl($mapscript);
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
// Figure out when we should start counting
$doy1 = date("j", mktime(0,0,0,9,1,$year) );
$doy2 = date("j", $ts);
$edate = date("Y-m-d", $ts);
if ($month >= 9) {
  $sdate = sprintf("%s-09-01", $year);
  $dateint = "extract(doy from valid) BETWEEN $doy1 and $doy2";
} else {
  $sdate = sprintf("%s-09-01", intval($year) - 1 );
  $dateint = "(extract(doy from valid) < $doy1 or extract(doy from valid) > $doy2)";
}

$data = Array();
$sql = "select station, min(valid) as v from hourly WHERE valid > '${sdate}' and c100 < 29 and valid < '${edate}' GROUP by station";
//echo $sql ."<br />";
$rs =  pg_exec($c, $sql);
for ($i=0; $row = @pg_fetch_array($rs,$i); $i++) {
  //$bdate = $row["v"];
  $bdate = $sdate;
  $key = $row["station"];
  if ($key == "A133259") continue;

  $data[$key]['name'] = $ISUAGcities[$key]['name'];
  $data[$key]['lon'] = $ISUAGcities[$key]['lon'];
  $data[$key]['lat'] = $ISUAGcities[$key]['lat'];

  $sql = "select count(distinct valid) as c from hourly 
      WHERE station = '$key' and valid > '$bdate' and valid < '$edate'
      and c100 >= 32 and c100 <= 45";
  //echo $sql ."<br />";
  $rs2 = pg_exec($c,$sql);
  if (pg_num_rows($rs2) == 0) continue;
  $r = pg_fetch_array($rs2,0);
  $val = $r["c"];

  $data[$key]['var'] = $val;

  // Calculate average?
  $syear = intval(date("Y", strtotime($ISUAGcities[$key]["archive_begin"])));
  $sql = "select count(distinct valid) as c 
       from hourly WHERE station = '$key' and c100 >= 32 and c100 <= 45 
       and extract(year from valid) > $syear and 
           extract(year from valid) < extract(year from now()) and
           $dateint ";
  //echo $sql ."<br />";
  $rs2 = pg_exec($c,$sql);
  if (pg_num_rows($rs2) == 0) continue;
  $r = pg_fetch_array($rs2,0);
  $avg = ($r["c"]) / (intval(date("Y")) - $syear -1);

  $data[$key]['var2'] = round($avg,0);


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

  $pt = ms_newPointObj();
  $pt->setXY($ISUAGcities[$key]['lon'], $ISUAGcities[$key]['lat'], 0);
  $pt->draw($map, $snet, $img, 2, "(".round($val - $avg,0).")");
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

mktitlelocal($map, $img, $height, "      Standard Chill Units [ $sdate thru ". date("Y-m-d", $ts) ." ]");
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
