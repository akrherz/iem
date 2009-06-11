<?php
/* Draw simple overview image */
include("../../config/settings.inc.php");
$extents = isset($_GET["BBOX"]) ? explode(",", $_GET["BBOX"]) : Array(-105,40,-97,47);

dl($mapscript);
$mapFile = $rootpath."/data/gis/base4326.map";
$map = ms_newMapObj($mapFile);
$map->set("width", 300);
$map->set("height",130);

$map->setExtent(-126,24,-66,50);

$img = $map->prepareImage();

$namerica = $map->getlayerbyname("namerica");
$namerica->set("status", MS_ON);
$namerica->draw($img);

$lakes = $map->getlayerbyname("lakes");
$lakes->set("status", MS_ON);
$lakes->draw($img);


$states = $map->getlayerbyname("states");
$states->set("status", MS_ON);
$states->draw($img);

/* Now we draw a box */
$rect = $map->getlayerbyname("rect");
$rect->set("status", MS_ON);
$rt = ms_newRectObj();
$rt->setextent($extents[0], $extents[1], $extents[2], $extents[3]);
$rt->draw($map, $rect, $img, 0, " ");
$rt->free();


header ("Content-type: image/png");
$img->saveImage('');


?>
