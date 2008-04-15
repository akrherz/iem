<?php
/* Tis my job to produce pretty maps with lots of options :) */
include("../../config/settings.inc.php");

/* Straight CGI Butter */
$sector = isset($_GET["sector"]) ? $_GET["sector"] : "iem";

$sectors = Array(
 "iem" => Array("epsg" => 4326, "ext" => Array(-100.0, 38.5, -88.0, 46.5)),
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

$counties = $map->getlayerbyname("uscounties");
$counties->set("status", MS_ON);
$counties->draw($img);

$states = $map->getlayerbyname("states");
$states->set("status", MS_ON);
$states->draw($img);

/* Draw NEXRAD Layer */
$radar = $map->getlayerbyname("nexrad_n0r");
$radar->set("status", MS_ON);
$radar->draw($img);

/* Watch by County */
$wbc = $map->getlayerbyname("watch_by_county");
$wbc->set("status", MS_ON);
$wbc->set("data", "g from (select phenomena, eventid, multi(geomunion(geom)) as g from warningsWHERE significance = 'A' and phenomena IN ('TO','SV') and issue <= now() and expire > now() GROUP by phenomena, eventid ORDER by phenomena ASC) as foo using SRID=4326 using unique phenomena");
$wbc->draw($img);


$sbw = $map->getlayerbyname("sbw");
$sbw->set("status", MS_ON);
$sbw->draw($img);

$bar640t = $map->getLayerByName("bar640t");
$bar640t->set("status", 1);
$bar640t->draw($img);

$tlayer = $map->getLayerByName("bar640t-title");
$point = ms_newpointobj();
$point->setXY(80, 12);
$point->draw($map, $tlayer, $img, 0,"NEXRAD Base Reflectivity");
$point->free();

$point = ms_newpointobj();
$point->setXY(80, 29);
$d = strftime("%d %B %Y %-2I:%M %p %Z" ,  time());
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
