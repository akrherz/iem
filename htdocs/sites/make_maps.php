<?php 
/* Draw a bunch of reference maps */

$map = ms_newMapObj("$rootpath/data/gis/base4326.map");
$map->set("width", 320);
$map->set("height", 240);
$lat0 = $metadata["lat"];
$lon0 = $metadata["lon"];
$map->setextent($lon0 - 5,$lat0 - 5,$lon0 + 5,$lat0 + 5);

$namer = $map->getlayerbyname("namerica");
$namer->set("status", 1);
$lakes = $map->getlayerbyname("lakes");
$lakes->set("status", 1);

$stlayer = $map->getlayerbyname("states");
$stlayer->set("status", 1);

$img = $map->prepareImage();
$namer->draw($img);
$lakes->draw($img);
$stlayer->draw($img);

$lyr = ms_newLayerObj($map);
$lyr->set("type", MS_SHAPE_POINT);
$lyr->set("status", MS_ON);
$lyr->set("labelcache", MS_ON);

$lyr_c0 = ms_newClassObj($lyr);
$lyr_c0s0 = ms_newStyleObj($lyr_c0);
$lyr_c0s0->set("symbolname", "circle");
$lyr_c0s0->set("size", 10);
$lyr_c0s0->color->setRGB(0,0,0);
$lyr_c0s1 = ms_newStyleObj($lyr_c0);
$lyr_c0s1->set("symbolname", "circle");
$lyr_c0s1->set("size", 6);
$lyr_c0s1->color->setRGB(255,0,0);

$lyr_c0->label->set("buffer", 20);
$lyr_c0->label->set("type", MS_BITMAP);
$lyr_c0->label->set("size", MS_GIANT);
$lyr_c0->label->set("position", MS_AUTO);
$lyr_c0->label->color->setRGB(255,255,255);
$lyr_c0->label->outlinecolor->setRGB(0,0,0);
$logopt = ms_newpointobj();
$logopt->setXY($lon0, $lat0);
$logopt->draw($map, $lyr, $img, 0, $metadata["name"]);
$logopt->free();

$map->drawLabelCache($img);

$url = $img->saveWebImage();

?><img src="<?php echo $url; ?>">
