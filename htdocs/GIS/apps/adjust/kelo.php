<body bgcolor="black">
<?php

dl("php_mapscript.so");

$map = ms_newMapObj("kelo.map");

$radar = $map->getlayerbyname("radar");
$radar->set("status", MS_ON);

$states = $map->getlayerbyname("states");
$states->set("status", MS_ON);

$counties = $map->getlayerbyname("counties");
$counties->set("status", MS_ON);

$locs = $map->getlayerbyname("kcci");
$locs->set("status", MS_ON);

$img = $map->prepareImage();
//$radar->draw($img);
$states->draw($img);
$locs->draw($img);

$map->drawLabelCache($img);
$url = $img->saveWebImage(MS_PNG, 0,0,-1);

echo "<img src=\"$url\">";


?>
