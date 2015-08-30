<?php
include_once("../../../../config/settings.inc.php");
include_once "../../../../include/iemmap.php";
include_once "../../../../include/database.inc.php";
include("../../../../include/network.php");

$year = isset($_GET["year"]) ? $_GET["year"]: date("Y", time() - 86400 - (7 * 3600) );
$month = isset($_GET["month"]) ? $_GET["month"]: date("m", time() - 86400 - (7 * 3600) );
$day = isset($_GET["day"]) ? $_GET["day"]: date("d", time() - 86400 - (7 * 3600) );
$date = isset($_GET["date"]) ? $_GET["date"]: $year ."-". $month ."-". $day;
$pvar = (isset($_GET["pvar"]) && $_GET["pvar"] != "" ) ? $_GET["pvar"] : "c11";
$network = isset($_REQUEST["network"]) ? strtoupper($_REQUEST["network"]): 'AUTO';
$ts = strtotime($date);

$networkopts = Array("AUTO", "ISUAG", "ISUSM");
if (! in_array($network, $networkopts)){
	die("Invalid network!");
}
if ($network == 'AUTO'){
	$network = 'ISUAG';
	if ($ts > strtotime("2013-09-01")){
		$network = 'ISUSM';
	}
}

$nt = new NetworkTable($network);

$varDef = Array("c11" => "High Air Temperatures",
  "c12" => "Low Air Temperatures [F]",
  "c11,c12" => "High and Low Air Temperatures [F]",
  "c30" => "Avg 4in Soil Temperatures [F]",
  "c40" => "Avg Wind Velocity [MPH]",
  "c509" => "Peak 1 Minute Gust [MPH]",
  "c529" => "Peak 5 Second Gust [MPH]",
  "c930" => "Total Precipitation [inch]",
  "c90" => "Total Precipitation [inch]",
  "c20" => "Avg Relative Humidity",
  "c80" => "Solar Radiation [Langleys]",
  "c70" => "Evapotranspiration [inch]",
  "dwpf" => "Dew Point [F]",
  "c300h,c300l" => "High and Low 4in Soil Temps [F]",
  "c529,c530" => "Peak 5 Sec Wind Gust [mph] and Time",
);

$rnd = Array("c11,c12" => 0, "c11" => 0, "c12" => 0, "c30" => 0,
		"c300h,c300l" => 0, "c509" => 1, "c20" => 0, "dwpf" => 0,
  "c70" => 2, "c40" => 1 ,"c80" => 0, "dwpfl,dwpfh" => 0,
  "c90" => 2, "c529,c530" => 2, "pmonth" => 2, "pday" => 2);


$map = ms_newMapObj("../../../../data/gis/base26915.map");
$map->setProjection("init=epsg:26915");
$map->setsize(640, 480);
$map->setextent(175000, 4440000, 775000, 4890000);


$counties = $map->getlayerbyname("counties");
$counties->set("status", MS_ON);

$snet = $map->getlayerbyname("station_plot");
$snet->set("status", MS_ON);

$iards = $map->getlayerbyname("iards");
$iards->set("status", MS_ON);

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

$c = iemdb("isuag");
$tbl = strftime("t%Y", $ts);
$dstamp = strftime("%Y-%m-%d", $ts);
if ($network == 'ISUAG'){
	if ($pvar == 'c300h,c300l') {
  		$q = "SELECT station, max(c300) as c300h, max(c300_f) as c300h_f,
     min(c300) as c300l, max(c300_f) as c300l_f
     from hourly WHERE date(valid) = '${dstamp}' GROUP by station";
	} else if ($pvar == 'dwpf') {
		$q = "select station,
		avg(k2f( dewpt( f2k(c100), c200))::numeric(7,2)) as dwpf,
		'' as dwpf_f
		from hourly WHERE c200 > 0 and date(valid) = '${dstamp}' GROUP by station";
	} else if ($pvar == 'dwpfh,dwpfl') {
		$q = "select MAX( k2f( dewpt( f2k(c100), c200)))::numeric(7,2) as dwpfh,
      station, MIN( k2f( dewpt( f2k(c100), c200)))::numeric(7,2) as dwpfl,
      max(c100_f) as dwpfh_f, max(c100_f) as dwpfl_f
      from hourly WHERE c200 > 0 and date(valid) = '${dstamp}' GROUP by station";
	} else if ($pvar == "c529,c530") {
  		$q = "SELECT station, c529, c529_f, 
    substring(text(c530),length(text(c530)) - 3,2) || ':' || 
    substring(text(c530), length(text(c530)) - 1,2) as c530 , 
    c530_f from daily WHERE valid = '${dstamp}' ";
	} else {
  		$q = "SELECT * from daily WHERE valid = '${dstamp}' ";
	}  
} else {
	$hourlyvars = Array("c20", "c300h,c300l");
	
	if (in_array($pvar, $hourlyvars)){
		$q = <<<EOF
  SELECT station,
  max(c2f(tsoil_c_avg)) as c300h, '' as c300h_f,
  min(c2f(tsoil_c_avg)) as c300l, '' as c300l_f,
  avg(rh) as c20, '' as c20_f
  from sm_hourly
	WHERE valid BETWEEN '${dstamp} 00:00' and '${dstamp} 23:59'
			GROUP by station
EOF;
	} else {
		$q = <<<EOF
  SELECT station, 
  c2f(tair_c_max) as c11, '' as c11_f,
  c2f(tair_c_min) as c12, '' as c12_f,
  c2f(tsoil_c_avg) as c30, '' as c30_f,
  ws_mps_s_wvt * 2.236 as c40, '' as c40_f,
  ws_mps_max * 2.236 as c509, '' as c509_f,
  ws_mps_max * 2.236 as c529, '' as c529_f,
  to_char(ws_mps_tmx, 'HH24MI') as c530, '' as c530_f,
  slrmj_tot as c80, '' as c80_f,
  dailyet / 24.5 as c70, '' as c70_f,
  rain_mm_tot * 24.5 as c90, '' as c90_f from sm_daily 
	WHERE valid = '${dstamp}' 
EOF;
	}
}
$rs =  pg_exec($c, $q);
$data = Array();
for ($i=0; $row = @pg_fetch_assoc($rs,$i); $i++) {
  $key = $row['station'];
  if ($key == "A133259") continue;

  // Red Dot... 
  $pt = ms_newPointObj();
  $pt->setXY($nt->table[$key]['lon'], $nt->table[$key]['lat'], 0);
  $pt->draw($map, $ponly, $img, 0);

  if (strpos($pvar, ',') !== false){
  	// Value UL
  	list($p1,$p2) = explode(",", $pvar);
  	$pt = ms_newPointObj();
  	$pt->setXY($nt->table[$key]['lon'], $nt->table[$key]['lat'], 0);
  	$pt->draw($map, $snet, $img, 1, 
    	 round($row[$p1], $rnd[$pvar]) ." ". $row[$p1 .'_f'] );


  	// Value LL
  	$pt = ms_newPointObj();
  	$pt->setXY($nt->table[$key]['lon'], $nt->table[$key]['lat'], 0);
  	$pt->draw($map, $snet, $img, 2, 
   	     round($row[$p2], $rnd[$pvar]) ." ". $row[$p2 .'_f'] );

  } else {
  	
  	// Value UL
  	$pt = ms_newPointObj();
  	$pt->setXY($nt->table[$key]['lon'], $nt->table[$key]['lat'], 0);
  	$pt->draw($map, $snet, $img, 1,
  			round($row[$pvar], $rnd[$pvar]) ." ". $row[$pvar .'_f'] );
  	 
  }
  
  // City Name
  $pt = ms_newPointObj();
  $pt->setXY($nt->table[$key]['lon'], $nt->table[$key]['lat'], 0);
  if ($key == "A131909" || $key == "A130209"){
    $pt->draw($map, $snet, $img, 0, $nt->table[$key]['name'] );
  } else {
    $pt->draw($map, $snet, $img, 0, $nt->table[$key]['name'] );
  }

}

iemmap_title($map, $img, $varDef[$pvar] ." on ". date("d M Y", $ts),
	($i == 0) ? 'No Data Found!': null );
$map->drawLabelCache($img);

header("Content-type: image/png");
$img->saveImage('');
?>