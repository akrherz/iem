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
 $point->setXY(50, 30);
                                                                                
 $point->draw($map, $layer, $imgObj, "logo", "");
}

function mktitle($map, $imgObj, $titlet) {
  $layer = $map->getLayerByName("credits");
                                                                                
  // point feature with text for location
  $point = ms_newpointobj();
  $point->setXY(9, 18);
                                                                                
  $point->draw($map, $layer, $imgObj, "credits",
    $titlet);
}




$map = ms_newMapObj("stations.map");
//iowa
//$map->setExtent(-97.5,40.5,-89.5,43.5);
$map->setExtent(-96.1,39.6,-94.4,41.3);
// E CONUS
//$map->setExtent(-130,16,-72,70);
//$map->setExtent(-99.4, 30.3,-95.0, 34.3);
//$map->setExtent(-84.2, 25.7,-80.7, 30.2);
//$map->setExtent(-100.92, 38.83, -97.06, 42.04);
//$map->setExtent(-103.37, 38.05,-99.40, 40.63);
//$map->setExtent(-90,29,-72,33);
//CLAYTON $map->setExtent(-92,42.5,-91.1,43.3);
//$map->setExtent(-93.5,42.0,-92.8,42.6);
$map->setSize(320,280);
$map->selectOutputFormat("PNG24");

$namer = $map->getlayerbyname("namerica");
$namer->set("status", MS_ON);

$lakes = $map->getlayerbyname("lakes");
$lakes->set("status", MS_OFF);

$states = $map->getlayerbyname("states");
$states->set("status", MS_ON);

$iembox = $map->getlayerbyname("iembox");
$iembox->set("status", MS_ON);

$counties = $map->getlayerbyname("counties");
$counties->set("status", MS_ON);

$terra = $map->getlayerbyname("terra");
$terra->set("status", MS_ON);

$maxdbz = $map->getlayerbyname("maxdbz");
$maxdbz->set("status", MS_ON);
$maxdbz->set("transparency", 70);

$bars = $map->getlayerbyname("bars");
$bars->set("status", MS_ON);

$dm = $map->getlayerbyname("dm");
$dm->set("status", MS_OFF);

$warnings0_c = $map->getlayerbyname("warnings0_c");
$warnings0_c->set("status", MS_OFF);
//$warnings0_c->set("data", "g from (select phenomena, eventid, multi(ST_union(geom)) as g from warnings_2008 WHERE significance = 'A' and phenomena IN ('TO','SV') and issue < '2008-04-10 20:00' and expire > '2008-04-10 20:00' GROUP by phenomena, eventid ORDER by phenomena ASC) as foo using SRID=4326 using unique phenomena");
//$warnings0_c->set("data", "geom from (select phenomena,  geom, oid from warnings WHERE gtype = 'P' and wfo = 'GLD' and significance = 'W' and phenomena in ('SV','TO') and issue > '2007-10-01') as foo USING unique oid using SRID=4326");
$warnings0_c->set("data", "geom from (select phenomena,  geom, oid from warnings_2011 WHERE gtype = 'P' and significance = 'W' and phenomena in ('SV','TO') and issue > '2011-04-03 19:00' and issue < '2011-04-05 19:00') as foo USING unique oid using SRID=4326");



$cwa = $map->getlayerbyname("cwa");
$cwa->set("status", MS_OFF);

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

$locs = $map->getlayerbyname("locs");
$locs->set("status", MS_OFF);

$cities = $map->getlayerbyname("sites");
$cities->set("status", MS_ON);

$watches = $map->getlayerbyname("watches");
$watches->set("status", MS_OFF);
$watches->set("data", "geom from (select type as wtype, geom, oid from watches WHERE extract(year from expired) = 2009 ORDER by type ASC) as foo");

$iards = $map->getlayerbyname("iards");
$iards->set("status", MS_OFF);
$iards_label = $map->getlayerbyname("iards_label");
$iards_label->set("status", MS_OFF);

$img = $map->prepareImage();
$namer->draw($img);
//$roads->draw($img);
//$iards->draw($img);
//$iards_label->draw($img);
//$dm->draw($img);
$lakes->draw($img);
//$watches->draw($img);
$terra->draw($img);
//$maxdbz->draw($img);
//$warnings0_c->draw($img);
$counties->draw($img);
$states->draw($img);
$cities->draw($img);
//$iembox->draw($img);

//$map->embedLegend($img);
$map->drawLabelCache($img);
$bars->draw($img);

mktitle($map, $img, "25 August 2011 Terra MODIS True Color _ 18 August 2011 Reported Hail Size [in]");
//mkl($map, $img);
$url = $img->saveWebImage();

echo "<form method=\"GET\" action=\"adjust.php\">
<input type=\"text\" name=\"d\" value=\"$d\">
<input type=\"submit\"><br />";

echo "<img src=\"$url\">";

//print_r($map->extent);
?>
