<body bgcolor="white">
<?php
set_time_limit(200);


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
  $point->setXY(0, 22);
                                                                                
  $point->draw($map, $layer, $imgObj, "credits",
    $titlet);
}


dl("php_mapscript_442.so");

$map = ms_newMapObj("stations.map");
$map->set("height", 768);
$map->set("width", 1024);

$namer = $map->getlayerbyname("namerica");
$namer->set("status", MS_ON);

$lakes = $map->getlayerbyname("lakes");
$lakes->set("status", MS_ON);

$states = $map->getlayerbyname("states");
$states->set("status", MS_ON);

$counties = $map->getlayerbyname("counties");
$counties->set("status", MS_ON);

$locs = $map->getlayerbyname("isabel");
$locs->set("status", MS_ON);

$bars = $map->getlayerbyname("bars");
$bars->set("status", MS_ON);

$w0c = $map->getlayerbyname("warnings0_c");
$w0c->set("status", MS_ON);

/**
$cwa = $map->getlayerbyname("cwa");
$cwa->set("status", MS_ON);

$cwa->queryByAttributes("WFO", "DMX", MS_SINGLE);
$cwa->open();
$rs = $cwa->getresult(0);
$shp = $cwa->getShape(-1, $rs->shapeindex);

$rect = $shp->bounds;
$projin = ms_newprojectionobj("init=epsg:4326");
$projout = ms_newprojectionobj("init=epsg:26915");
$rect->project($projin, $projout);
*/

// Top side margin
//$map->setextent($rect->minx, $rect->miny, 
//  $rect->maxx + 50000, $rect->maxy + 50000);

//$roads = $map->getlayerbyname("topo");
//$roads->set("status", MS_ON);

$cities = $map->getlayerbyname("sites");
$cities->set("status", MS_ON);

$watches = $map->getlayerbyname("watches");
$watches->set("status", MS_ON);

$iards = $map->getlayerbyname("iards");
$iards->set("status", MS_ON);
$iards_label = $map->getlayerbyname("iards_label");
$iards_label->set("status", MS_ON);

$img = $map->prepareImage();
$namer->draw($img);
$lakes->draw($img);
//$counties->draw($img);
//$roads->draw($img);
//$iards->draw($img);
//$iards_label->draw($img);
//$w0c->draw($img);
$watches->draw($img);
$states->draw($img);
//$cities->draw($img);

$map->drawLabelCache($img);
//$bars->draw($img);

mktitle($map, $img, "                     2005 NWS Watches (unofficial) [thru 3 Jun]  Tornado (Red), Svr Thunder (Yellow) ");
mkl($map, $img);

$url = $img->saveWebImage(MS_PNG, 0,0,-1);


echo "<img src=\"$url\">";

//print_r($map->extent);
?>
