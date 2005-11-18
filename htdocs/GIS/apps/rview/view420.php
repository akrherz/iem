<?php

dl("php_mapscript_401.so");

include("lib.php");

$map = ms_newMapObj("mosaic420.map");

$radar = $map->getlayerbyname("radar");
$radar->set("status", MS_ON);

$states = $map->getlayerbyname("states");
$states->set("status", MS_ON);

$w0c = $map->getlayerbyname("warnings0_c");
$w0c->set("status", MS_ON);

$w0p = $map->getlayerbyname("warnings0_p");
$w0p->set("status", MS_ON);

$counties = $map->getlayerbyname("counties");
$counties->set("status", MS_ON);

$img = $map->prepareImage();
$states->draw($img);
$counties->draw($img);
$radar->draw($img);
$w0c->draw($img);
$w0p->draw($img);

$ts = @filemtime("/mesonet/data/gis/images/unproj/USCOMP/n0r_0.png");
$d = date("d F Y h:i A" ,  $ts + 15);

mktitle($map, $img, "                  IEM NEXRAD composite base reflect valid: $d");
$map->drawLabelCache($img);
mklogolocal($map, $img);

header("Content-type: image/png");
$img->saveImage('', MS_PNG, 0, 0, -1);
?>
