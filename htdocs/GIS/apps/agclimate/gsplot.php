<?php
require_once "../../../../config/settings.inc.php";
require_once "../../../../include/iemmap.php";
require_once "../../../../include/database.inc.php";
require_once "../../../../include/network.php";

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

if ($year > 2013) {
	$nt = new NetworkTable("ISUSM");
	$ISUAGcities = $nt->table;
} else {
	$nt = new NetworkTable("ISUAG");
	$ISUAGcities = $nt->table;
	$ISUAGcities["A130219"]["lon"] += 0.2;
}

$vineyard = Array('GVNI4', 'AHTI4', 'BNKI4', 'CSII4', 'OSTI4');

$gs_start = mktime(0,0,0,$smonth,$sday,$year);
$gs_end = mktime(0,0,0,$emonth,$eday,$year);

$round = Array("prec" => 2, "gdd50" => 0, "gdd32" => 0, "et" => 2, 
	"sgdd50" => 0, "sgdd52" => 0, "sdd86" => 0, "srad" => 0);

$today = time();
if ($gs_end >= $today)  $gs_end = $today;

$emonth = strftime("%m", $gs_end);
$eday = strftime("%d", $gs_end);
$smonth = strftime("%m", $gs_start);
$sday = strftime("%d", $gs_start);

$varDef = Array(
  "gdd32" => "Growing Degree Days (base=32)",
  "gdd41" => "Growing Degree Days (base=41)",
  "gdd46" => "Growing Degree Days (base=46)",
  "gdd48" => "Growing Degree Days (base=48)",
  "gdd50" => "Growing Degree Days (base=50)",
  "gdd51" => "Growing Degree Days (base=51)",
  "gdd52" => "Growing Degree Days (base=52)",
  "et" => "Potential Evapotranspiration",
  "prec" => "Precipitation",
  "srad" => "Solar Radiation (langleys)",
  "sgdd50" => "Soil Growing Degree Days (base=50)",
  "sgdd52" => "Soil Growing Degree Days (base=52)",
  "sdd86" => "Stress Degree Days (base=86)"
);



$rnd = Array(
  "gdd32" => 0,
  "gdd41" => 0,
  "gdd46" => 0,
  "gdd48" => 0,
  "gdd50" => 0,
  "gdd51" => 0,
  "gdd52" => 0,
  "et" => 2, "c11" => 2,
  "prec" => 2,
  "srad" => 0,
  "sgdd50" => 0,
  "sgdd52" => 0,
  "sdd86" => 0);

$myStations = $ISUAGcities;
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
foreach($ISUAGcities as $key => $val){
  $csite = $ISUAGcities[$key]["climate_site"];
  $climate[$key] = Array('gdd32'=> 0, 'gdd50' => 0, 'sdd86'=>0, 'prec'=>0,
    'gdd41' => 0, 'gdd46' => 0, 'gdd48' => 0, 'gdd51' => 0, 'gdd52' => 0);

  $sql = sprintf("SELECT * from climate51 WHERE station = '%s' and
    valid BETWEEN '%s' and '%s'", $csite, $cStart, $cEnd);
  $rs =  pg_exec($climatedb, $sql);
  for ($i=0; $row = pg_fetch_array($rs); $i++) {
    $climate[$key]['gdd32'] += $row["gdd32"];
    $climate[$key]['gdd41'] += $row["gdd41"];
    $climate[$key]['gdd46'] += $row["gdd46"];
    $climate[$key]['gdd48'] += $row["gdd48"];
    $climate[$key]['gdd50'] += $row["gdd50"];
    $climate[$key]['gdd51'] += $row["gdd51"];
    $climate[$key]['gdd52'] += $row["gdd52"];
    $climate[$key]['prec'] += $row["precip"];
 
  }
}

// sigh
if (substr($var, 0, 3) == 'gdd') {
  $level = intval(substr($var, 3, 2));
	if ($year > 2013){
		$q = <<<EOF
  SELECT station, c2f(tair_c_max) as c11, c2f(tair_c_min) as c12 from sm_daily
  WHERE valid >= '{$sstr}' and valid < '{$estr}'
EOF;
	} else {
  		$q = <<<EOF
  SELECT station, c11, c12 from daily
  WHERE valid >= '{$sstr}' and valid < '{$estr}'
EOF;
	}
  
  $gdds = Array();
  $rs =  pg_exec($c, $q);
  for ($i=0; $row = pg_fetch_array($rs); $i++) {
    $stid = $row['station'];
    $high = (float)$row['c11'];
    $low  = (float)$row['c12'];
    $tgdd = gdd($high, $low, 86, $level);

    if (! isset($gdds[$stid]) ) $gdds[$stid] = 0;
    $gdds[$stid] = $gdds[$stid] + $tgdd;
  }
  $vals = $gdds;
} 
/* ------------------------------------------------------- */
if ($var == 'sdd86') {
	if ($year > 2013){
		$q = <<<EOF
  SELECT station, c2f(tair_c_max) as c11, c2f(tair_c_min) as c12 from sm_daily
  WHERE valid >= '{$sstr}' and valid < '{$estr}'
EOF;
	} else {
  		$q = <<<EOF
  SELECT station, c11, c12 from daily
  WHERE valid >= '{$sstr}' and valid < '{$estr}'
EOF;
	}

  $gdds = Array();
  $rs =  pg_exec($c, $q);
  for ($i=0; $row = pg_fetch_array($rs); $i++) {
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
else if ($var == 'sgdd50' || $var == 'sgdd52') {
	if ($year > 2013){
		$q = "SELECT station, date(valid) as dvalid, 
				c2f(max(tsoil_c_avg)) as high,
				c2f(min(tsoil_c_avg)) as low from sm_hourly WHERE
				valid >= '". $sstr ."'
     			and valid < '". $estr ."' GROUP by station, dvalid";	
	} else {
  		$q = "SELECT station, date(valid) as dvalid, 
     		max(c300) as high, min(c300) as low
     		from hourly WHERE valid >= '". $sstr ."'
     		and valid < '". $estr ."' GROUP by station, dvalid";
	}
  $gdds = Array();
  $rs =  pg_exec($c, $q);
  for ($i=0; $row = pg_fetch_array($rs); $i++) {
    $stid = $row['station'];
    $high = (float)$row['high'];
    $low  = (float)$row['low'];
    if ($var == 'sgdd50'){
    	$tgdd = gdd($high, $low, 86, 50);
    } else{
    	$tgdd = gdd($high, $low, 86, 52);
    }
    if (! isset($gdds[$stid]) ) $gdds[$stid] = 0;
    $gdds[$stid] = $gdds[$stid] + $tgdd;
  }
  $vals = $gdds;
}  
/* ------------------------------------------------------- */
else if ($var == 'et') {
	if ($year > 2013){
	$q = <<<EOF
	SELECT station, sum(dailyet / 24.5) as et from sm_daily
	WHERE valid >= '{$sstr}' and valid < '{$estr}' GROUP by station
EOF;
	} else {
  $q = "SELECT station, sum(c70) as et
     from daily WHERE valid >= '". $sstr ."'
     and valid < '". $estr ."' GROUP by station";
	}
  $vals = Array();
  $rs =  pg_exec($c, $q);
  for ($i=0; $row = pg_fetch_array($rs); $i++) {
    $stid = $row['station'];
    $vals[$stid] = $row['et'];
  }
}
/* ------------------------------------------------------- */
else if ($var == 'srad') {
	if ($year > 2013){
  $q = "SELECT station, sum(slrmj_tot) as srad
     from sm_daily WHERE valid >= '". $sstr ."'
     and valid < '". $estr ."' GROUP by station";
	} else {
		$q = "SELECT station, sum(c80) as srad
     from daily WHERE valid >= '". $sstr ."'
     and valid < '". $estr ."' GROUP by station";
	}

  $vals = Array();
  $rs =  pg_exec($c, $q);
  for ($i=0; $row = pg_fetch_array($rs); $i++) {
    $stid = $row['station'];
    $vals[$stid] = $row['srad'];
  }
}
/* ------------------------------------------------------- */
else if ($var == 'prec') {
	if ($year > 2013){
		$q = "SELECT station, sum(rain_mm_tot / 24.5) as prec
     from sm_daily WHERE valid >= '". $sstr ."'
     and valid < '". $estr ."' GROUP by station";
	} else {
  $q = "SELECT station, sum(c90) as prec
     from daily WHERE valid >= '". $sstr ."'
     and valid < '". $estr ."' GROUP by station";
	}
  $vals = Array();
  $rs =  pg_exec($c, $q);
  for ($i=0; $row = pg_fetch_array($rs); $i++) {
    $stid = $row['station'];
    $vals[$stid] = $row['prec'];
  }
}  
/* ------------------------------------------------------- */

foreach($vals as $key => $value){
  if ($key == "A133259") continue;
  if (in_array($key, $vineyard)) continue;


  // Red Dot... 
  $pt = ms_newPointObj();
  $pt->setXY($ISUAGcities[$key]['lon'], $ISUAGcities[$key]['lat'], 0);
  $pt->draw($map, $ponly, $img, 0);

  // Value UL
  $pt = ms_newPointObj();
  $pt->setXY($ISUAGcities[$key]['lon'], $ISUAGcities[$key]['lat'], 0);
  $pt->draw($map, $snet, $img, 1, round($value, $rnd[$var]) );

  // Climate
  if (substr($var, 0, 3) == "gdd" || $var == "prec")
  {
    $pt = ms_newPointObj();
    $pt->setXY($ISUAGcities[$key]['lon'], $ISUAGcities[$key]['lat'], 0);
    $pt->draw($map, $snet, $img, 2, "(". round($value - $climate[$key][$var],$rnd[$var]) .")");

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
  }

  // City Name
  $pt = ms_newPointObj();
  $pt->setXY($ISUAGcities[$key]['lon'], $ISUAGcities[$key]['lat'], 0);
  $ar = explode("-", $ISUAGcities[$key]['name']);
  if ($key == "A131909" || $key == "A130209"){
    $pt->draw($map, $snet, $img, 0,  $ar[0]);
  } else {
    $pt->draw($map, $snet, $img, 0, $ar[0] );
  }
}

iemmap_title($map, $img, $year." ". $varDef[$var] , 
	"(". $sstr_txt ." - ". $estr_txt .")");
$map->drawLabelCache($img);

header("Content-type: image/png");
$img->saveImage('');

?>
