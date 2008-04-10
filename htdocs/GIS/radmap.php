<?php
/* Tis my job to produce pretty maps with lots of options :) */
include("../../config/settings.inc.php");

$epsg = 2163;

dl($mapscript);

$map = ms_newMapObj($rootpath."/data/gis/base${epsg}.map");
$map->set("width", 640);
$map->set("height",480);
//US $map->setExtent(-2110437, -2251067, 2548326, 1239063);
$map->setExtent(-632031.375, -2133488,623680.125, -959689.625);

$img = $map->prepareImage();

$namerica = $map->getlayerbyname("namerica");
$namerica->set("status", MS_ON);
$namerica->draw($img);

$lakes = $map->getlayerbyname("lakes");
$lakes->set("status", MS_ON);
$lakes->draw($img);

$counties = $map->getlayerbyname("counties");
$counties->set("status", MS_ON);
$counties->draw($img);

$states = $map->getlayerbyname("states");
$states->set("status", MS_ON);
$states->draw($img);

/* Draw NEXRAD Layer */
$radar = $map->getlayerbyname("radar");
$radar->set("status", MS_ON);
$radar->draw($img);
$ts = @filemtime("/home/ldm/data/gis/images/4326/USCOMP/n0r_0.png");
if ($ts == 0 || $ts == "") {
  sleep(10);
  $ts = @filemtime("/mesonet/data/gis/images/4326/USCOMP/n0r_0.png");
}
$d = strftime("%d %B %Y %-2I:%M %p %Z" ,  $ts + 15);

$sbw = $map->getlayerbyname("sbw");
$sbw->set("status", MS_ON);
$sbw->draw($img);

$watches = $map->getlayerbyname("watches");
$watches->set("status", MS_ON);
$watches->draw($img);

$bar640t = $map->getLayerByName("bar640t");
$bar640t->set("status", 1);
$bar640t->draw($img);

$tlayer = $map->getLayerByName("bar640t-title");
$point = ms_newpointobj();
$point->setXY(80, 12);
$point->draw($map, $tlayer, $img, 0,"NEXRAD Base Reflectivity");
$point->free();
$point = ms_newpointobj();
$point->setXY(80, 29);
$point->draw($map, $tlayer, $img, 1,"$d");
$point->free();

$map->drawLabelCache($img);

$layer = $map->getLayerByName("logo");
$point = ms_newpointobj();
$point->setXY(40, 26);
$point->draw($map, $layer, $img, "logo", "");
$point->free();

$layer = $map->getLayerByName("n0r-ramp");
$point = ms_newpointobj();
$point->setXY(560, 15);
$point->draw($map, $layer, $img, "n0r-ramp", "");
$point->free();


header("Content-type: image/png");
$img->saveImage('');
?>
