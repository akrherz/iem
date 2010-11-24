<?php



include("lib.php");

$map = ms_newMapObj("base.map");
$map->selectoutputformat("png24");

$states = $map->getlayerbyname("states");
$states->set("status", MS_ON);

$w0c = $map->getlayerbyname("warnings0_c");
$w0c->set("status", MS_ON);

$w0p = $map->getlayerbyname("warnings0_p");
$w0p->set("status", MS_ON);

$counties = $map->getlayerbyname("counties");
$counties->set("status", MS_ON);

$img = $map->prepareImage();
$w0c->draw($img);
$states->draw($img);
$counties->draw($img);
//$w0p->draw($img);

mktitle($map, $img, "                    Flash Flood Warnings: 21 May thru 23 May 2004");
$map->drawLabelCache($img);
mklogolocal($map, $img);

header("Content-type: image/png");
$img->saveImage('');
?>
