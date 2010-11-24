<?php



include("lib.php");

$map = ms_newMapObj("radar.map");
$map->setExtent(-89671, -713811, 1034764, 183473);
$map->setSize(640,480);

$radar = $map->getlayerbyname("radar");
$radar->set("status", MS_ON);

$namerica = $map->getlayerbyname("namerica");
$namerica->set("status", MS_ON);

$lakes = $map->getlayerbyname("lakes");
$lakes->set("status", MS_ON);
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

$img = $map->prepareImage();
$namerica->draw($img);
$lakes->draw($img);
$radar->draw($img);
$counties->draw($img);
$states->draw($img);
$watches->draw($img);
$w0c->draw($img);
$w0p->draw($img);

$ts = @filemtime("/mesonet/data/gis/images/unproj/USCOMP/n0r_0.png");
$d = date("d F Y h:i A" ,  $ts + 15);

mktitle($map, $img, "                  IEM NEXRAD composite base reflect valid: $d");
$map->drawLabelCache($img);
mklogolocal($map, $img);

header("Content-type: image/png");
$img->saveImage('test.png', MS_PNG, 0, 0, -1);
?>
