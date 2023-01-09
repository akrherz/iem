<?php
require_once "/usr/lib64/php/modules/mapscript.php";

require_once "../../../../config/settings.inc.php";

$map = new mapObj("robins.map");

$counties = $map->getlayerbyname("counties");
$counties->__set("status", MS_ON);

$robins = $map->getlayerbyname("robins");
$robins->__set("status", MS_ON);

$img = $map->prepareImage();

$counties->draw($map, $img);
$robins->draw($map, $img);

$map->drawLabelCache($img);

header("Content-type: image/png");
echo $img->getBytes();
