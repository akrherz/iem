<body bgcolor="#EEEEEE">

<?php

dl("php_mapscript.so");

$map = ms_newMapObj("simple.map");

$counties = $map->getlayerbyname("counties");
$counties->set("status", MS_ON);

$erosion = $map->getlayerbyname("erosion");
$erosion->set("status", MS_ON);

$iatwp = $map->getlayerbyname("iatwp");
$iatwp->set("status", MS_ON);

$ppoints = $map->getlayerbyname("temp");
$ppoints->set("status", MS_ON);

$background = $map->getlayerbyname("background");
$background->set("status", MS_ON);

$img = $map->prepareImage();

//$background->draw($img);
$counties->draw($img);
$erosion->draw($img);
//$iatwp->draw($img);

$url = $img->saveWebImage(MS_PNG, 0,0,-1);

echo "<img src=\"$url\">";

echo $url;
?>
