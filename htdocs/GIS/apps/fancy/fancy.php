<?php

dl("php_mapscript.so");

$map = ms_newMapObj("fancy.map");

//$map->setextent(-83760, -2587, 478797, 433934);
$map->setextent(-100.1, 35.15, -89.9, 43.85);

$layer = $map->getlayerbyname("temps");
$layer->set("status", MS_ON);

$background = $map->getlayerbyname("background");
$background->set("status", MS_ON);

$sname = $map->getlayerbyname("sname");
$sname->set("status", MS_ON);

$warnly = $map->getlayerbyname("warnings0");
$warnly->set("status", MS_ON);

$stlayer = $map->getlayerbyname("states");
$stlayer->set("status", 1);

$green = $map->addColor(0, 255, 0);
$blue = $map->addColor(0, 0, 255);
$black = $map->addColor(0, 0, 0);
$white = $map->addColor(255, 255, 255);
//$trans = $map->addColor(1, 1, 1);

$st_cl = ms_newclassobj($stlayer);
$st_cl->set("outlinecolor", $green);
$st_cl->set("status", MS_ON);

$img = $map->prepareImage();

$ly = ms_newlayerobj($map);
$ly->set("status", MS_ON);
$ly->set("type", MS_LAYER_POINT);
$ly->setProjection("proj=latlong");

$cl = ms_newclassobj($ly);
$cl->set("status", MS_ON);
$cl->set("name", "ccc");
$cl->set("symbol", 1);
$cl->set("size", 10);
$cl->set("color", $green);
$cl->set("backgroundcolor", $green);

$lbl = $cl->label;
$lbl->set("type", MS_TRUETYPE);
$lbl->set("antialias", MS_OFF);
$lbl->set("font", "arial");
$lbl->set("size", 18);
$lbl->set("color", $black);
$lbl->set("position", MS_AUTO);
$lbl->set("force", MS_ON);

$ly2 = $map->getLayerByName("pointonly");
$ly2->set("status", MS_ON);
$ly2->setProjection("proj=latlong");

$background->draw( $img);
$stlayer->draw( $img);
$warnly->draw( $img);
$layer->draw($img);
$sname->draw($img);

//$pt = ms_newPointObj();
//$pt->setXY(-95, 42, 0);
//$pt->draw($map, $ly, $img, 0, "test_point");
//$pt->free();

//$pt = ms_newPointObj();
//$pt->setXY(-94, 42, 0);
//$pt->draw($map, $ly2, $img, 0, "");
//$pt->free();

//$layer2->draw($img);
//$ly->draw( $img);

//$img = $map->draw();
$map->drawLabelCache($img);

$url = $img->saveWebImage(MS_PNG, 0,0,-1);

$im = @imagecreatefrompng("/mesonet/www/html/". $url );

ImageTTFText($im, 22, 0, 150, 330, $white, "./kcci.ttf", "Current Temperatures");

ImagePng($im , "/mesonet/www/html/". $url );
ImageDestroy($im);


echo "<img src=\"$url\">";


?>


