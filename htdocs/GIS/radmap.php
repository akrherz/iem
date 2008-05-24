<?php
/* Tis my job to produce pretty maps with lots of options :) */
include("../../config/settings.inc.php");

/* Straight CGI Butter */
$sector = isset($_GET["sector"]) ? $_GET["sector"] : "iem";

$sectors = Array(
 "iem" => Array("epsg" => 4326, "ext" => Array(-100.0, 38.5, -88.0, 46.5)),
 "lot" => Array("epsg" => 4326, "ext" => Array(-94.8, 39.0, -83.5, 46.5)),
 "ict" => Array("epsg" => 4326, "ext" => Array(-102.4, 35.45, -94.4, 40.35)),
 "sd" => Array("epsg" => 4326, "ext" => Array(-105.5, 40.5, -95.5, 48.0)),
 "hun" => Array("epsg" => 4326, "ext" => Array(-90.0, 32.0, -84.0, 36.0)),
 "conus" => Array("epsg" => 2163, 
         "ext" => Array(-2110437, -2251067, 2548326, 1239063)),
 "texas" => Array("epsg" => 2163, 
         "ext" => Array(-532031.375, -2133488,723680.125, -959689.625)),
);

/* Could define a custom box */
if (isset($_GET["bbox"]))
{
  $sector = "custom";
  $bbox = isset($_GET["bbox"]) ? explode(",",$_GET["bbox"]) : die("No BBOX");
  $sectors["custom"] = Array("epsg"=> 4326, "ext" => $bbox);
}


/* Lets determine our timestamp.  This is rather important. */
$ts = isset($_GET["ts"]) ? gmmktime(
 substr($_GET["ts"],8,2), substr($_GET["ts"],10,2), 0,
 substr($_GET["ts"],4,2), substr($_GET["ts"],6,2), substr($_GET["ts"],0,4)): 0;


/* Lets Plot stuff already! */
dl($mapscript);

$mapFile = $rootpath."/data/gis/base".$sectors[$sector]['epsg'].".map";
$map = ms_newMapObj($mapFile);
$map->set("width", 640);
$map->set("height",480);
$map->setExtent($sectors[$sector]['ext'][0],
                $sectors[$sector]['ext'][1], 
                $sectors[$sector]['ext'][2],
                $sectors[$sector]['ext'][3]);

$img = $map->prepareImage();

$namerica = $map->getlayerbyname("namerica");
$namerica->set("status", MS_ON);
$namerica->draw($img);

$lakes = $map->getlayerbyname("lakes");
$lakes->set("status", MS_ON);
$lakes->draw($img);

/* Draw NEXRAD Layer */
$radar = $map->getlayerbyname("nexrad_n0r");
$radar->set("status", MS_ON);
if ($ts > 0){
 $radar->set("data", gmstrftime("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/uscomp/n0r_%Y%m%d%H%M.png", $ts) );
}
$radar->draw($img);

$counties = $map->getlayerbyname("uscounties");
$counties->set("status", MS_ON);
$counties->draw($img);

$states = $map->getlayerbyname("states");
$states->set("status", MS_ON);
$states->draw($img);


/* Watch by County */
$wbc = $map->getlayerbyname("watch_by_county");
$wbc->set("status", MS_ON);
$wbc->set("connection", "user=nobody dbname=postgis host=iemdb");
if ($ts > 0) {
  $sql = sprintf("g from (select phenomena, eventid, multi(geomunion(geom)) as g from warnings_%s WHERE significance = 'A' and phenomena IN ('TO','SV') and issue <= '%s:00+00' and expire > '%s:00+00' GROUP by phenomena, eventid ORDER by phenomena ASC) as foo using SRID=4326 using unique phenomena",gmstrftime("%Y",$ts),
  gmstrftime("%Y-%m-%d %H:%M", $ts), gmstrftime("%Y-%m-%d %H:%M", $ts) );
} else {
  $sql = "g from (select phenomena, eventid, multi(geomunion(geom)) as g from warnings WHERE significance = 'A' and phenomena IN ('TO','SV') and issue <= now() and expire > now() GROUP by phenomena, eventid ORDER by phenomena ASC) as foo using SRID=4326 using unique phenomena";
}
$wbc->set("data", $sql);
$wbc->draw($img);

/*
$watches = $map->getlayerbyname("watches");
$watches->set("status", MS_ON);
$watches->set("connection", "user=nobody dbname=postgis host=iemdb");
$watches->setFilter("expired > '2008-01-01'");
$watches->draw($img);
*/

$sbw = $map->getlayerbyname("sbw");
$sbw->set("status", MS_ON);
$sbw->set("connection", "user=nobody dbname=postgis host=iemdb");
$sbw->set("maxscale", 10000000);
if ($ts > 0)
{
  $sql = sprintf("geom from (select phenomena, geom, oid from warnings_%s 
  WHERE significance != 'A' and issue <= '%s:00+00' and expire > '%s:00+00' and 
  gtype = 'P') as foo using unique oid using SRID=4326", gmstrftime("%Y",$ts),
  gmstrftime("%Y-%m-%d %H:%M", $ts), gmstrftime("%Y-%m-%d %H:%M", $ts) );
} else {
  $sql = "geom from (select phenomena, geom, oid from warnings WHERE significance != 'A' and expire > CURRENT_TIMESTAMP and gtype = 'P') as foo using unique oid using SRID=4326";
}
$sbw->set("data", $sql);
$sbw->draw($img);

$bar640t = $map->getLayerByName("bar640t");
$bar640t->set("status", 1);
$bar640t->draw($img);

$tlayer = $map->getLayerByName("bar640t-title");
$point = ms_newpointobj();
$point->setXY(80, 12);
$point->draw($map, $tlayer, $img, 0,"NEXRAD Base Reflectivity");
//$point->draw($map, $tlayer, $img, 0,"2008 SPC Watch Boxes");
$point->free();

$point = ms_newpointobj();
$point->setXY(80, 29);
if ($ts > 0) { $d = strftime("%d %B %Y %-2I:%M %p %Z" ,  $ts); }
else { $d = strftime("%d %B %Y %-2I:%M %p %Z" ,  time()); }
$point->draw($map, $tlayer, $img, 1,"$d");
$point->free();

$map->drawLabelCache($img);

$layer = $map->getLayerByName("logo");
$point = ms_newpointobj();
$point->setXY(40, 26);
$point->draw($map, $layer, $img, "logo", "");
$point->free();

$layer = $map->getLayerByName("n0r-ramp");
$point = ms_newpointobj();
$point->setXY(560, 15);
$point->draw($map, $layer, $img, "n0r-ramp", "");
$point->free();


header("Content-type: image/png");
$img->saveImage('');
?>
