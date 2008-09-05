<?php
include("../../../../config/settings.inc.php");



function mkl($map, $imgObj) {
                                                                                
 $layer = $map->getLayerByName("logo");
                                                                                
 // point feature with text for location
 $point = ms_newpointobj();
 $point->setXY(50, 30);
                                                                                
 $point->draw($map, $layer, $imgObj, "logo", "");
}

function mktitle($map, $imgObj, $titlet) {
  $layer = $map->getLayerByName("credits");
                                                                                
  // point feature with text for location
  $point = ms_newpointobj();
  $point->setXY(6, 22);
                                                                                
  $point->draw($map, $layer, $imgObj, "credits",
    $titlet);
}


dl($mapscript);

$map = ms_newMapObj("stations.map");
$map->set("height", 300);
$map->set("width",  320);
$map->setExtent(-100.0, 37.5, -88.0, 45.5);

$namer = $map->getlayerbyname("namerica");
$namer->set("status", MS_ON);

$lakes = $map->getlayerbyname("lakes");
$lakes->set("status", MS_ON);

$states = $map->getlayerbyname("states");
$states->set("status", MS_ON);

$iembox = $map->getlayerbyname("iembox");
$iembox->set("status", MS_ON);

$counties = $map->getlayerbyname("counties");
$counties->set("status", MS_ON);


$bars = $map->getlayerbyname("bars");
$bars->set("status", MS_ON);

$wh = $map->getlayerbyname("watch_hours");
$wh->set("status", MS_ON);

$img = $map->prepareImage();
$namer->draw($img);
$wh->draw($img);
$lakes->draw($img);
$counties->draw($img);
//$watches->draw($img);
$states->draw($img);
$map->embedlegend($img);


$map->drawLabelCache($img);
//$bars->draw($img);

mktitle($map, $img, "         SVR/TOR Watch Hours 5/24-6/8 2008");
//mkl($map, $img);

$url = $img->saveWebImage();


echo "<img src=\"$url\">";

//print_r($map->extent);
?>
