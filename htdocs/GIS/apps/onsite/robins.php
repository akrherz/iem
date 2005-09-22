<?php
dl("php_mapscript_440.so");

$map = ms_newMapObj("robins.map");

$counties = $map->getlayerbyname("counties");
$counties->set("status", MS_ON);

$robins = $map->getlayerbyname("robins");
$robins->set("status", MS_ON);

$img = $map->prepareImage();

$counties->draw($img);
$robins->draw($img);

$map->drawLabelCache($img);

header("Content-type: image/png");
$img->saveImage('');


?>
