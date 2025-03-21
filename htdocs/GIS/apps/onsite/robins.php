<?php
require_once "../../../../config/settings.inc.php";
require_once "../../../../include/vendor/mapscript.php";


$map = new mapObj("robins.map");

$counties = $map->getLayerByName("counties");
$counties->__set("status", MS_ON);

$robins = $map->getLayerByName("robins");
$robins->__set("status", MS_ON);

$img = $map->prepareImage();

$counties->draw($map, $img);
$robins->draw($map, $img);

$map->drawLabelCache($img);

header("Content-type: image/png");
echo $img->getBytes();
