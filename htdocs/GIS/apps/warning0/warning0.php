<?php

dl("php_mapscript_36.so");

$map = ms_newMapObj("warning0.map");

$map->setextent(-1147166, -1286565, 1784179, 988198);

$layer = $map->getlayerbyname(warnings0);
$layer->set("status", 1);

$layer = $map->getlayerbyname(warnings1d);
$layer->set("status", 0);

$img = $map->draw();
$url = $img->saveWebImage("MS_PNG", 0,0,-1);



echo "<img src=\"$url\">";

?>


