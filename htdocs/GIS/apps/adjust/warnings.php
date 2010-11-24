<body bgcolor="white">
<?php
include("../../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");

$d = isset($_GET["d"]) ? $_GET["d"] : "1997-04-01";

set_time_limit(200);


function mkl($map, $imgObj) {
                                                                                
 $layer = $map->getLayerByName("logo");
                                                                                
 // point feature with text for location
 $point = ms_newpointobj();
 $point->setXY(40, 30);
                                                                                
 $point->draw($map, $layer, $imgObj, "logo", "");
}

function mktitle($map, $imgObj, $titlet) {
  $layer = $map->getLayerByName("credits");
                                                                                
  // point feature with text for location
  $point = ms_newpointobj();
  $point->setXY(40, 24);
                                                                                
  $point->draw($map, $layer, $imgObj, "credits",
    $titlet);
}




$map = ms_newMapObj("$rootpath/data/gis/base4326.map");
$map->setSize(768,1024);
//$map->setExtent(-98, 40, -90, 45);
//US $map->setExtent(-125, 29, -65, 49);
$map->setExtent(-95, 34, -75, 44);

$namer = $map->getlayerbyname("namerica");
$namer->set("status", MS_ON);

$lakes = $map->getlayerbyname("lakes");
$lakes->set("status", MS_ON);

$states = $map->getlayerbyname("states");
$states->set("status", MS_ON);


$counties = $map->getlayerbyname("uscounties");
$counties->set("status", MS_ON);


$warnings0_c = $map->getlayerbyname("sbw");
$warnings0_c->set("status", MS_ON);
$warnings0_c->set("connection", $_DATABASES["postgis"]);
$warnings0_c->set("data", "geom from (select phenomena, geom, oid from warnings_2009 WHERE significance != 'A' and phenomena in ('SV','TO') and issue > '2009-02-11 12:00' and issue < '2009-02-12 06:00' and gtype = 'P' ORDER by phenomena ASC) as foo using unique oid using SRID=4326");


/*
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


$img = $map->prepareImage();
$namer->draw($img);
$counties->draw($img);
//$roads->draw($img);
//$iards->draw($img);
//$iards_label->draw($img);
$lakes->draw($img);
//$watches->draw($img);
$warnings0_c->draw($img);
$states->draw($img);


mktitle($map, $img, "          Feb 11 12z - Feb 12 6z 2009 Storm Based Warnings");
$map->drawLabelCache($img);
mkl($map, $img);

$url = $img->saveWebImage();

echo "<form method=\"GET\" action=\"adjust.php\">
<input type=\"text\" name=\"d\" value=\"$d\">
<input type=\"submit\"><br />";

echo "<img src=\"$url\">";

//print_r($map->extent);
?>
