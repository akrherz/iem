<?php

dl("php_mapscript_401.so");

include("lib.php");

$map = ms_newMapObj("mosaic2.map");

$radar = $map->getlayerbyname("radar");
$radar->set("status", MS_ON);

$states = $map->getlayerbyname("states");
$states->set("status", MS_ON);

$watches = $map->getlayerbyname("watches");
$watches->set("status", MS_ON);

$w0c = $map->getlayerbyname("warnings0_c");
$w0c->set("status", MS_ON);

$w0p = $map->getlayerbyname("warnings0_p");
$w0p->set("status", MS_ON);

$counties = $map->getlayerbyname("counties");
$counties->set("status", MS_ON);

$nexattr = $map->getlayerbyname("nexattr");
$nexattr->set("status", MS_ON);

$img = $map->prepareImage();
$states->draw($img);
$counties->draw($img);
$radar->draw($img);
$nexattr->draw($img);
$watches->draw($img);
$w0c->draw($img);
$w0p->draw($img);

$ts = @filemtime("/mesonet/data/gis/images/unproj/MWCOMP/n0r_0.png");
$d = date("d F Y h:i A" ,  $ts + 15);

mktitle($map, $img, "                  IEM NEXRAD composite base reflect valid: $d");
$map->drawLabelCache($img);
mklogolocal($map, $img);

header("Content-type: image/png");
$img->saveImage('', MS_PNG, 0, 0, -1);
?>
