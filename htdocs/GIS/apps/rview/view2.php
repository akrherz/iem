<?php

dl("php_mapscript_401.so");

function mktitle($map, $imgObj, $titlet) {
  $layer = $map->getLayerByName("credits");

  // point feature with text for location
  $point = ms_newpointobj();
  $point->setXY(10, 15);

  $point->draw($map, $layer, $imgObj, "credits",
    $titlet);
}

function mklogolocal($map, $imgObj) { 
 
        $layer = $map->getLayerByName("logo");
 
       // point feature with text for location
       $point = ms_newpointobj();
       $point->setXY(44, 
                     24);

       $point->draw($map, $layer, $imgObj, "logo",
                     "");
}


$map = ms_newMapObj("mosaic.map");

//$map->setProjection("proj=latlong");
//$map->setextent(-124, 26, -66, 50);

$radar = $map->getlayerbyname("radar2");
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

$ts = filemtime("/mesonet/data/gis/images/unproj/MWCOMP/n0r_0.png");
$d = date("d F Y h:i A" ,  $ts);

mktitle($map, $img, "                  IEM NEXRAD composite base reflect valid: $d");
$map->drawLabelCache($img);
mklogolocal($map, $img);

header("Content-type: image/png");
$img->saveImage('', MS_PNG, 0, 0, -1);
?>
