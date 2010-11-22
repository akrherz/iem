<?php
include("../../../../config/settings.inc.php");

function mktitle($map, $imgObj, $titlet) {
  $layer = $map->getLayerByName("credits");

  // point feature with text for location
  $point = ms_newpointobj();
  $point->setXY( 120, 340);

  $point->draw($map, $layer, $imgObj, "credits",
    $titlet);
}

$map = ms_newMapObj("mosaic.map");
$map->setSize(300,350);

$map->setextent(-320000, -300000, 720000, 700000);

$states = $map->getlayerbyname("states");
$states->set("status", MS_ON);

$nex = $map->getlayerbyname("smooth_radar");
$nex->set("status", MS_ON);

$inex = $map->getlayerbyname("inex");
$inex->set("status", MS_ON);

$icwa = $map->getlayerbyname("icwa");
$icwa->set("status", MS_ON);

$img = $map->prepareImage();

$nex->draw($img);
$states->draw($img);
$inex->draw($img);
$icwa->draw($img);

$map->drawLabelCache($img);

$ts = @filemtime("/home/ldm/data/gis/images/4326/USCOMP/n0r_0.png");
  if ($ts == 0 || $ts == "")
  {
    sleep(10);
    $ts = @filemtime("/home/ldm/data/gis/images/4326/USCOMP/n0r_0.png");
  }
  $d = date("d F Y h:i A" ,  $ts + 15);


mktitle($map, $img, " ". $d ." ");

header("Content-type: image/png");
$img->saveImage('');
?>
