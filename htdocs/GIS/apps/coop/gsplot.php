<?php
/* Generate a plot based on a request from gsplot.phtml, no more tmp 
 * files please
 */
include("../../../../config/settings.inc.php");
include("../../../../include/database.inc.php");
$coopdb = iemdb("coop");
include("../../../../include/forms.php");
include("../../../../include/network.php");

$var = isset($_GET["var"]) ? $_GET["var"]: "gdd50";
$year = isset($_GET["year"]) ? $_GET["year"]: date("Y");
$smonth = isset($_GET["smonth"]) ? $_GET["smonth"]: 5;
$sday = isset($_GET["sday"]) ? $_GET["sday"]: 1;
$emonth = isset($_GET["emonth"]) ? $_GET["emonth"]: date("m");
$eday = isset($_GET["eday"]) ? $_GET["eday"]: date("d");
$network = isset($_REQUEST["network"]) ? $_REQUEST["network"]: "IACLIMATE";

$nt = new NetworkTable( $network );
$cities = $nt->table;


/** Need to use external date lib 
  * http://php.weblogs.com/adodb_date_time_library
  */
include("../../../../include/adodb-time.inc.php");

$sts = adodb_mktime(0,0,0,$smonth, $sday, $year);
$ets = adodb_mktime(0,0,0,$emonth, $eday, $year);

if ($sts > $ets){
	$sts = $ets - 86400;
}


function mktitlelocal($map, $imgObj, $titlet) { 
 
  $layer = $map->getLayerByName("credits");
 
     // point feature with text for location
  $point = ms_newpointobj();
  $point->setXY( 0, 10);
  $point->draw($map, $layer, $imgObj, 0, $titlet );
}

function plotNoData($map, $img){
  $layer = $map->getLayerByName("credits");

  $point = ms_newpointobj();
  $point->setXY( 100, 200);
  $point->draw($map, $layer, $img, 1,
    "  No data found for this date! ");

}

$varDef = Array("gdd50" => "Growing Degree Days (base=50)",
  "et" => "Potential Evapotranspiration",
  "prec" => "Precipitation",
  "sgdd50" => "Soil Growing Degree Days (base=50)",
  "sdd86" => "Stress Degree Days (base=86)",
  "mintemp" => "Minimum Temperature [F]",
  "maxtemp" => "Maximum Temperature [F]",
);



$rnd = Array("gdd50" => 0,
  "et" => 2,
  "prec" => 2,
  "sgdd50" => 0,
  "sdd86" => 0,
  "mintemp" => 0,
  "maxtemp" => 0);
$myStations = $cities;
$height = 480;
$width = 640;

$proj = "init=epsg:26915";

$map = ms_newMapObj("../../../../data/gis/base26915.map");
$map->setProjection($proj);

$state = substr($network,0,2);
$dbconn = iemdb("postgis");
$rs = pg_query($dbconn, "SELECT ST_xmin(g), ST_xmax(g), ST_ymin(g), ST_ymax(g) from (
		select ST_Extent(ST_Transform(the_geom,26915)) as g from states 
		where state_abbr = '${state}'
		) as foo");
$row = pg_fetch_array($rs,0);
$buf = 35000; // 35km
$xsz = $row[1] - $row[0];
$ysz = $row[3] - $row[2];
if (($ysz + 100000) > $xsz){
	$map->setsize(600,800);
} else {
	$map->setsize(800,600);
}
$map->setextent($row[0] - $buf, $row[2] - $buf,
		$row[1] + $buf, $row[3] + $buf);

$counties = $map->getlayerbyname("counties");
$counties->set("status", MS_ON);

$states = $map->getlayerbyname("states");
$states->set("status", MS_ON);

$bar640t = $map->getlayerbyname("bar640t");
$bar640t->set("status", MS_ON);

$snet = $map->getlayerbyname("snet");
$snet->set("status", MS_ON);

$iards = $map->getlayerbyname("iards");
$iards->set("status", 1);

$ponly = $map->getlayerbyname("pointonly");
$ponly->set("status", MS_ON);

$img = $map->prepareImage();
$counties->draw($img);
$states->draw($img);
$iards->draw($img);
$bar640t->draw($img);

$rs = pg_prepare($coopdb, "SELECT", "SELECT station, 
	sum(precip) as s_prec, sum(gdd50(high,low)) as s_gdd50,
	sum(sdd86(high,low)) as s_sdd86, min(low) as s_mintemp,
	max(high) as s_maxtemp from alldata 
	WHERE day >= $1 and day <= $2 GROUP by station 
	ORDER by station ASC");
$rs = pg_execute($coopdb, "SELECT", Array(adodb_date("Y-m-d", $sts),
	adodb_date("Y-m-d", $ets)));
	
for($i=0;$row=@pg_fetch_array($rs,$i);$i++){
	
	$ukey = $row["station"];
	if (! isset($cities[$ukey]) ) continue;
		  	  // Red Dot...  
  $pt = ms_newPointObj();
  $pt->setXY($cities[$ukey]['lon'], $cities[$ukey]['lat'], 0);
  $pt->draw($map, $ponly, $img, 0);

  // City Name
  $pt = ms_newPointObj();
  $pt->setXY($cities[$ukey]['lon'], $cities[$ukey]['lat'], 0);
  $pt->draw($map, $snet, $img, 3, $cities[$ukey]['name'] );

		  // Value UL
  $pt = ms_newPointObj();
  $pt->setXY($cities[$ukey]['lon'], $cities[$ukey]['lat'], 0);
  $pt->draw($map, $snet, $img, 0,
     round($row["s_".$var], $rnd[$var]) );

  
  
	}
if ($i == 0)
   plotNoData($map, $img);

   $title = sprintf("%s (%s through %s)", $varDef[$var], adodb_date("Y-m-d", $sts),
	adodb_date("Y-m-d", $ets));
   
mktitlelocal($map, $img, $title);
$map->drawLabelCache($img);

header("Content-type: image/png");
$img->saveImage('');
?>