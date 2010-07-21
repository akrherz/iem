<?php
include("../../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/network.php");
$nt = new NetworkTable("ISUAG");
$ISUAGcities = $nt->table;
$ISUAGcities["A130219"]["lon"] += 0.2;

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

$gs_start = mktime(0,0,0,$smonth,$sday,$year);
$gs_end = mktime(0,0,0,$emonth,$eday,$year);

$round = Array("prec" => 2, "gdd50" => 0, "gdd32" => 0, "et" => 2, "sgdd50" => 0, "sdd86" => 0, "srad" => 0);

$today = time();
if ($gs_end >= $today)  $gs_end = $today;

$emonth = strftime("%m", $gs_end);
$eday = strftime("%d", $gs_end);
$smonth = strftime("%m", $gs_start);
$sday = strftime("%d", $gs_start);

dl($mapscript);
include("lib.php");

$varDef = Array("gdd50" => "Growing Degree Days (base=50)",
  "gdd32" => "Growing Degree Days (base=32)",
  "et" => "Potential Evapotranspiration",
  "prec" => "Precipitation",
  "srad" => "Solar Radiation (langleys)",
  "sgdd50" => "Soil Growing Degree Days (base=50)",
  "sdd86" => "Stress Degree Days (base=86)"
);



$rnd = Array("gdd50" => 0,
  "gdd32" => 0,
  "et" => 2, "c11" => 2,
  "prec" => 2,
  "srad" => 0,
  "sgdd50" => 0,
  "sdd86" => 0);


$myStations = $ISUAGcities;
$height = $height;
$width = $width;

$proj = "init=epsg:26915";

$map = ms_newMapObj("base.map");
$map->setsize($width,$height);
$map->setProjection($proj);

$map->setextent(175000, 4440000, 775000, 4890000);


$counties = $map->getlayerbyname("counties");
$counties->set("status", MS_ON);

$snet = $map->getlayerbyname("snet");
$snet->set("status", MS_ON);
$sclass = $snet->getClass(0);

$iards = $map->getlayerbyname("iards");
$iards->set("status", MS_ON);


$ponly = $map->getlayerbyname("pointonly");
$ponly->set("status", MS_ON);

$img = $map->prepareImage();
$counties->draw($img);
$iards->draw($img);

$c = iemdb("isuag");
$climatedb = iemdb("coop");

$sstr = strftime("%Y-%m-%d", $gs_start);
$estr = strftime("%Y-%m-%d", $gs_end);
$cStart = "2000". strftime("-%m-%d", $gs_start);
$cEnd = "2000". strftime("-%m-%d", $gs_end);
$sstr_txt = strftime("%b %d", $gs_start);
$estr_txt = strftime("%b %d", $gs_end);

function gdd($high, $low, $ceiling, $floor)
{
  if ($low < $floor)    $low = $floor;
  if ($high > $ceiling) $high = $ceiling;
  if ($high < $floor) return 0;

  return (($high+$low)/2.00) - $floor;
}

/* -------- Lets compute the climatology ------ */
$climate = Array();
reset($ISUAGcities);
while( list($key,$val) = each($ISUAGcities) ) {
  $csite = strtolower($ISUAGcities[$key]["climate_site"]);
  $climate[$key] = Array('gdd32'=> 0, 'gdd50' => 0,'sdd86'=>0,'prec'=>0);

  $sql = sprintf("SELECT * from climate51 WHERE station = '%s' and
    valid BETWEEN '%s' and '%s'", $csite, $cStart, $cEnd);
  $rs =  pg_exec($climatedb, $sql);
  for ($i=0; $row = @pg_fetch_array($rs,$i); $i++) {
    $climate[$key]['gdd32'] += gdd($row["high"],$row["low"],86,32);
    $climate[$key]['gdd50'] += gdd($row["high"],$row["low"],86,50);
    $climate[$key]['prec'] += $row["precip"];
 
  }
}

/* ------------------------------------------------------- */
if ($var == 'gdd32') {
  $q = "SELECT station, c11, c12
     from daily WHERE valid >= '". $sstr ."'
     and valid < '". $estr ."'";

  $gdds = Array();
  $rs =  pg_exec($c, $q);
  for ($i=0; $row = @pg_fetch_array($rs,$i); $i++) {
    $stid = $row['station'];
    $high = (float)$row['c11'];
    $low  = (float)$row['c12'];
    $tgdd = gdd($high, $low, 86, 32);

    if (! isset($gdds[$stid]) ) $gdds[$stid] = 0;
    $gdds[$stid] = $gdds[$stid] + $tgdd;
  }
  $vals = $gdds;
} 
/* ------------------------------------------------------- */
if ($var == 'gdd50') {
  $q = "SELECT station, c11, c12
     from daily WHERE valid >= '". $sstr ."'
     and valid < '". $estr ."'";

  $gdds = Array();
  $rs =  pg_exec($c, $q);
  for ($i=0; $row = @pg_fetch_array($rs,$i); $i++) {
    $stid = $row['station'];
    $high = (float)$row['c11'];
    $low  = (float)$row['c12'];
    $tgdd = gdd($high, $low, 86, 50);

    if (! isset($gdds[$stid]) ) $gdds[$stid] = 0;
    $gdds[$stid] = $gdds[$stid] + $tgdd;
  }
  $vals = $gdds;
}  
/* ------------------------------------------------------- */
if ($var == 'sdd86') {
  $q = "SELECT station, c11, c12
     from daily WHERE valid >= '". $sstr ."'
     and valid < '". $estr ."'";

  $gdds = Array();
  $rs =  pg_exec($c, $q);
  for ($i=0; $row = @pg_fetch_array($rs,$i); $i++) {
    $stid = $row['station'];
    $high = (float)$row['c11'];
    $low  = (float)$row['c12'];
    $tgdd = gdd($high, $low, 186, 86);

    if (! isset($gdds[$stid]) ) $gdds[$stid] = 0;
    $gdds[$stid] = $gdds[$stid] + $tgdd;
  }
  $vals = $gdds;
}  
/* ------------------------------------------------------- */
else if ($var == 'sgdd50') {
  $q = "SELECT station, date(valid) as dvalid, 
     max(c300) as high, min(c300) as low
     from hourly WHERE valid >= '". $sstr ."'
     and valid < '". $estr ."' GROUP by station, dvalid";

  $gdds = Array();
  $rs =  pg_exec($c, $q);
  for ($i=0; $row = @pg_fetch_array($rs,$i); $i++) {
    $stid = $row['station'];
    $high = (float)$row['high'];
    $low  = (float)$row['low'];
    $tgdd = gdd($high, $low, 86, 50);

    if (! isset($gdds[$stid]) ) $gdds[$stid] = 0;
    $gdds[$stid] = $gdds[$stid] + $tgdd;
  }
  $vals = $gdds;
}  
/* ------------------------------------------------------- */
else if ($var == 'et') {
  $q = "SELECT station, sum(c70) as et
     from daily WHERE valid >= '". $sstr ."'
     and valid < '". $estr ."' GROUP by station";

  $vals = Array();
  $rs =  pg_exec($c, $q);
  for ($i=0; $row = @pg_fetch_array($rs,$i); $i++) {
    $stid = $row['station'];
    $vals[$stid] = $row['et'];
  }
}
/* ------------------------------------------------------- */
else if ($var == 'srad') {
  $q = "SELECT station, sum(c80) as srad
     from daily WHERE valid >= '". $sstr ."'
     and valid < '". $estr ."' GROUP by station";

  $vals = Array();
  $rs =  pg_exec($c, $q);
  for ($i=0; $row = @pg_fetch_array($rs,$i); $i++) {
    $stid = $row['station'];
    $vals[$stid] = $row['srad'];
  }
}
/* ------------------------------------------------------- */
else if ($var == 'prec') {
  $q = "SELECT station, sum(c90) as prec
     from daily WHERE valid >= '". $sstr ."'
     and valid < '". $estr ."' GROUP by station";

  $vals = Array();
  $rs =  pg_exec($c, $q);
  for ($i=0; $row = @pg_fetch_array($rs,$i); $i++) {
    $stid = $row['station'];
    $vals[$stid] = $row['prec'];
  }
}  
/* ------------------------------------------------------- */


$tr = "# ".$year." ". $varDef[$var] ." (". $sstr_txt ." - ". $estr_txt .")\n";
$tr .= "#-----------------------snip------------------\n";
$tr .= sprintf("%20s,%10s,%10s,%10s\n", 'StationName', 'Latitude', 'Longitude', $var);
foreach($vals as $key => $value){
  if ($key == "A133259") continue;

  $tr .= sprintf("%20s,%.4f,%.4f,%10s\n", $ISUAGcities[$key]['name'],
  $ISUAGcities[$key]['lat'], $ISUAGcities[$key]['lon'], round($value, $round[$var]) );

  // Red Dot... 
  $pt = ms_newPointObj();
  $pt->setXY($ISUAGcities[$key]['lon'], $ISUAGcities[$key]['lat'], 0);
  $pt->draw($map, $ponly, $img, 0, ' ' );
  $pt->free();

  // Value UL
  $pt = ms_newPointObj();
  $pt->setXY($ISUAGcities[$key]['lon'], $ISUAGcities[$key]['lat'], 0);
  $pt->draw($map, $snet, $img, 0, 
     round($value, $rnd[$var]) );
  $pt->free();

  // Climate
  if ($var == "gdd32" || $var == "gdd50" || $var == "prec")
  {
    $pt = ms_newPointObj();
    $pt->setXY($ISUAGcities[$key]['lon'], $ISUAGcities[$key]['lat'], 0);
    $pt->draw($map, $snet, $img, 2, "(". round($value - $climate[$key][$var],$rnd[$var]) .")");
    $pt->free();

  }

  if (isset($_GET["var2"])) {
    // Value LL
    $pt = ms_newPointObj();
    $pt->setXY($ISUAGcities[$key]['lon'], $ISUAGcities[$key]['lat'], 0);
    if ($var2 == 'c530'){
      $pt->draw($map, $snet, $img, 2, 
        $row[$var2] ." ". $row[$var2 .'_f'] );
    } else {
      $pt->draw($map, $snet, $img, 2, 
        round($row[$var2], $rnd[$var2]) ." ". $row[$var2 .'_f'] );
    }
    $pt->free();
  }

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

mktitlelocal($map, $img, $height, "      ".$year." ". $varDef[$var] ." (". $sstr_txt ." - ". $estr_txt .") ");
$map->drawLabelCache($img);
$layer = $map->getLayerByName("logo");
$point = ms_newpointobj();
$point->setXY( 37, 27);
$point->draw($map, $layer, $img, 0, "");
$point->free();

header("Content-type: image/png");
$img->saveImage('');

?>
