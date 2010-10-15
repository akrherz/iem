<?php
/* Generate a plot based on a request from gsplot.phtml, no more tmp 
 * files please
 */
include("../../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$coopdb = iemdb("coop");
include("$rootpath/include/forms.php");
include("$rootpath/include/network.php");
$nt = new NetworkTable("IACLIMATE");
$cities = $nt->table;

$var = isset($_GET["var"]) ? $_GET["var"]: "gdd50";
$year = isset($_GET["year"]) ? $_GET["year"]: date("Y");
$smonth = isset($_GET["smonth"]) ? $_GET["smonth"]: 5;
$sday = isset($_GET["sday"]) ? $_GET["sday"]: 1;
$emonth = isset($_GET["emonth"]) ? $_GET["emonth"]: date("m");
$eday = isset($_GET["eday"]) ? $_GET["eday"]: date("d");

/** Need to use external date lib 
  * http://php.weblogs.com/adodb_date_time_library
  */
include("$rootpath/include/adodb-time.inc.php");

$sts = adodb_mktime(0,0,0,$smonth, $sday, $year);
$ets = adodb_mktime(0,0,0,$emonth, $eday, $year);


dl($mapscript);

function mktitlelocal($map, $imgObj, $titlet) { 
 
  $layer = $map->getLayerByName("credits");
 
     // point feature with text for location
  $point = ms_newpointobj();
  $point->setXY( 0, 10);
  $point->draw($map, $layer, $imgObj, 0,
    $titlet ."                                                                                ");
  $point->free();

     // point feature with text for location
  $point = ms_newpointobj();
  $point->setXY( 0, 460);
  $point->draw($map, $layer, $imgObj, 1,
    "  Iowa Environmental Mesonet | NWS COOP ");
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

$map = ms_newMapObj("base.map");
$map->setProjection($proj);

$map->setextent(250000, 4450000, 690000, 4880000);

$counties = $map->getlayerbyname("counties");
$counties->set("status", MS_ON);

$snet = $map->getlayerbyname("snet");
$snet->set("status", MS_ON);

$iards = $map->getlayerbyname("iards");
$iards->set("status", 1);

$ponly = $map->getlayerbyname("pointonly");
$ponly->set("status", MS_ON);

$img = $map->prepareImage();
$counties->draw($img);
$iards->draw($img);

$rs = pg_prepare($coopdb, "SELECT", "SELECT stationid, 
	sum(precip) as s_prec, sum(gdd50(high,low)) as s_gdd50,
	sum(sdd86(high,low)) as s_sdd86, min(low) as s_mintemp,
	max(high) as s_maxtemp from alldata 
	WHERE day >= $1 and day < $2 GROUP by stationid 
	ORDER by stationid ASC");
$rs = pg_execute($coopdb, "SELECT", Array(adodb_date("Y-m-d", $sts),
	adodb_date("Y-m-d", $ets)));
	
for($i=0;$row=@pg_fetch_array($rs,$i);$i++){
	
	$ukey = strtoupper($row["stationid"]);
	if (! isset($cities[$ukey]) ) continue;
		  	  // Red Dot...  
  $pt = ms_newPointObj();
  $pt->setXY($cities[$ukey]['lon'], $cities[$ukey]['lat'], 0);
  $pt->draw($map, $ponly, $img, 0, '' );
  $pt->free();

  // City Name
  $pt = ms_newPointObj();
  $pt->setXY($cities[$ukey]['lon'], $cities[$ukey]['lat'], 0);
  $pt->draw($map, $snet, $img, 1, $cities[$ukey]['name'] );
  $pt->free();
		  // Value UL
  $pt = ms_newPointObj();
  $pt->setXY($cities[$ukey]['lon'], $cities[$ukey]['lat'], 0);
  $pt->draw($map, $snet, $img, 0,
     round($row["s_".$var], $rnd[$var]) );
  $pt->free();
  
  
	}
if ($i == 0)
   plotNoData($map, $img);

   $title = sprintf("%s (%s - %s)", $varDef[$var], adodb_date("Y-m-d", $sts),
	adodb_date("Y-m-d", $ets));
   
mktitlelocal($map, $img, $title);
$map->drawLabelCache($img);

header("Content-type: image/png");
$img->saveImage('');
?>