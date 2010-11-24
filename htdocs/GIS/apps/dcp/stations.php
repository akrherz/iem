<body bgcolor="#000000">
<?php

function mktitle($map, $imgObj, $titlet) {
  $layer = $map->getLayerByName("credits");

  // point feature with text for location
  $point = ms_newpointobj();
  $point->setXY( 0,
                     40);

  $point->draw($map, $layer, $imgObj, "credits",
    $titlet);
}



$map = ms_newMapObj("stations.map");

$counties = $map->getlayerbyname("counties");
$counties->set("status", MS_ON);

$dcp = $map->getlayerbyname("dcp");
$dcp->set("status", MS_ON);

$river = $map->getlayerbyname("rivers");
$river->set("status", MS_ON);


$img = $map->prepareImage();
$counties->draw($img);
$river->draw($img);
$dcp->draw($img);

$map->drawLabelCache($img);
mktitle($map, $img, " NE Iowa DCP Sites                 
                                   ");

$url = $img->saveWebImage(MS_PNG, 0,0,-1);

echo "<img src=\"$url\">";


?>
