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
  $point->setXY(0, 22);
                                                                                
  $point->draw($map, $layer, $imgObj, "credits",
    $titlet);
}


dl($mapscript);

$map = ms_newMapObj("stations.map");
$map->set("height", 1024);
$map->set("width",  1280);

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

$locs = $map->getlayerbyname("locs");
$locs->set("status", MS_OFF);
$locs->set("connection", $_DATABASES["mesosite"]);

$bars = $map->getlayerbyname("bars");
$bars->set("status", MS_ON);

$dm = $map->getlayerbyname("dm");
$dm->set("status", MS_ON);

$warnings0_c = $map->getlayerbyname("warnings0_c");
$warnings0_c->set("status", MS_ON);

$cwa = $map->getlayerbyname("cwa");
$cwa->set("status", MS_ON);

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

$cities = $map->getlayerbyname("sites");
$cities->set("status", MS_OFF);

$watches = $map->getlayerbyname("watches");
$watches->set("status", MS_OFF);
$watches->set("data", "geom from (select type as wtype, geom, oid from watches WHERE extract(year from expired) = 2005 and type = 'TOR' ORDER by type ASC) as foo");

$iards = $map->getlayerbyname("iards");
$iards->set("status", MS_OFF);
$iards_label = $map->getlayerbyname("iards_label");
$iards_label->set("status", MS_OFF);

$img = $map->prepareImage();
$namer->draw($img);
//$counties->draw($img);
//$roads->draw($img);
//$iards->draw($img);
//$iards_label->draw($img);
//$dm->draw($img);
$lakes->draw($img);
$warnings0_c->draw($img);
$watches->draw($img);
$states->draw($img);
$cwa->draw($img);
$locs->draw($img);
//$iembox->draw($img);

$map->drawLabelCache($img);
//$bars->draw($img);

mktitle($map, $img, "         2005 Severe Thunderstorm Warnings (County)");
//mkl($map, $img);

$url = $img->saveWebImage();

echo "<form method=\"GET\" action=\"adjust.php\">
<input type=\"text\" name=\"d\" value=\"$d\">
<input type=\"submit\"><br />";

echo "<img src=\"$url\">";

//print_r($map->extent);
?>
