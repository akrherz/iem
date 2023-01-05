<?php
require_once "/usr/lib64/php/modules/mapscript.php";
/*
 * Draw a map of the CONUS with a simple box showing the area of interest
 */
require_once "../../config/settings.inc.php";
$extents = isset($_GET["BBOX"]) ? explode(",", $_GET["BBOX"]) : 
    Array(-105,40,-97,47);

$mapFile = "../../data/gis/base4326.map";
$map = new mapObj($mapFile);
$map->setSize(300,130);

$map->setExtent(-126,24,-66,50);

$img = $map->prepareImage();

$namerica = $map->getlayerbyname("namerica");
$namerica->__set("status", MS_ON);
$namerica->draw($map, $img);

$lakes = $map->getlayerbyname("lakes");
$lakes->__set("status", MS_ON);
$lakes->draw($map, $img);

$states = $map->getlayerbyname("states");
$states->__set("status", MS_ON);
$states->draw($map, $img);

/* Now we draw a box */
$rect = $map->getlayerbyname("rect");
$rect->__set("status", MS_ON);
$rt = new rectObj($extents[0], $extents[1], $extents[2], $extents[3]);
$rt->draw($map, $rect, $img, 0, " ");

header ("Content-type: image/png");
echo $img->getBytes();
