<?php
include("../../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");

$year = isset($_GET["year"]) ? $_GET["year"]: date("Y", time() - 86400 - (7 * 3600) );
$month = isset($_GET["month"]) ? $_GET["month"]: date("m", time() - 86400 - (7 * 3600) );
$day = isset($_GET["day"]) ? $_GET["day"]: date("d", time() - 86400 - (7 * 3600) );
$date = isset($_GET["date"]) ? $_GET["date"]: $year ."-". $month ."-". $day;


$direct = isset($_GET["direct"]) ? $_GET['direct']: "";

$ts = strtotime($date);

dl($mapscript);
include("$rootpath/include/agclimateLoc.php");

function mktitlelocal($map, $imgObj, $titlet) { 
 
  $layer = $map->getLayerByName("credits");
 
     // point feature with text for location
  $point = ms_newpointobj();
  $point->setXY( 0, 10);
  $point->draw($map, $layer, $imgObj, 0,
    $titlet ."                                                           ");
  $point->free();

     // point feature with text for location
  $point = ms_newpointobj();
  $point->setXY( 0, 330);
  $point->draw($map, $layer, $imgObj, 1,
    "  Iowa Environmental Mesonet | Iowa State Ag Climate Network ");
  $point->free();
}

function plotNoData($map, $img){
  $layer = $map->getLayerByName("credits");

  $point = ms_newpointobj();
  $point->setXY( 100, 200);
  $point->draw($map, $layer, $img, 1,
    "  No data found for this date! ");
  $point->free();

}

$myStations = $ISUAGcities;
$height = 350;
$width = 450;

$proj = "proj=tmerc,lat_0=41.5,lon_0=-93.65,x_0=0,y_0=0,k=0.9999";

$map = ms_newMapObj("base.map");
$map->setProjection($proj);

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
if ($month >= 9) {
  $sdate = sprintf("%s-09-01", $year);
  $dateint = "extract(doy from valid) BETWEEN $doy1 and $doy2";
} else {
  $sdate = sprintf("%s-09-01", intval($year) - 1 );
  $dateint = "(extract(doy from valid) < $doy1 or extract(doy from valid) > $doy2)";
}
$sql = "select station, min(valid) as v from hourly WHERE valid > '${sdate}' and c100 < 29 GROUP by station";
$rs =  pg_exec($c, $sql);
for ($i=0; $row = @pg_fetch_array($rs,$i); $i++) {
  $bdate = $row["v"];
  $key = $row["station"];
  if ($key == "A133259" || $key == "A130219") continue;

  $sql = "select count(distinct valid) as c from hourly 
      WHERE station = '$key' and valid > '$bdate' 
      and c100 >= 32 and c100 <= 45";
  $rs2 = pg_exec($c,$sql);
  if (pg_num_rows($rs2) == 0) continue;
  $r = pg_fetch_array($rs2,0);
  $val = $r["c"];

  // Calculate average?
  $syear = intval(date("Y", $ISUAGcities[$key]["sts"]));
  $sql = "select count(distinct valid) as c 
       from hourly WHERE station = '$key' and c100 >= 32 and c100 <= 45 
       and extract(year from valid) > $syear and 
           extract(year from valid) < $year and
           $dateint ";
  $rs2 = pg_exec($c,$sql);
  if (pg_num_rows($rs2) == 0) continue;
  $r = pg_fetch_array($rs2,0);
  $avg = ($r["c"]) / ($year - $syear -1);


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
  $pt->draw($map, $snet, $img, 1, $ISUAGcities[$key]['city'] );
  $pt->free();
}
if ($i == 0)
   plotNoData($map, $img);

mktitlelocal($map, $img, "  Standard Chill Units [ $sdate thru ". date("Y-m-d", $ts) ."  ]");
$map->drawLabelCache($img);

$url = $img->saveWebImage();

if (strlen($direct) > 0) { 
  header("Content-type: image/png");
  $img->saveImage('');
} else {
?>
<img src="<?php echo $url; ?>" border=1>

<?php } ?>
