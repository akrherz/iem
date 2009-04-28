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


dl($mapscript);

$map = ms_newMapObj("stations.map");
$map->set("height", 240);
$map->set("width",  320);
$map->setExtent(-97, 37.5, -86, 44.5);
//$map->setExtent(-125, 29, -65, 49);

$namer = $map->getlayerbyname("namerica");
$namer->set("status", MS_ON);

$lakes = $map->getlayerbyname("lakes");
$lakes->set("status", MS_ON);

$states = $map->getlayerbyname("states");
$states->set("status", MS_ON);


$counties = $map->getlayerbyname("uscounties");
$counties->set("status", MS_ON);


$warnings0_c = $map->getlayerbyname("river");
$warnings0_c->set("status", MS_ON);
$warnings0_c->set("connection", $_DATABASES["postgis"]);


$img = $map->prepareImage();
$namer->draw($img);
$counties->draw($img);
//$roads->draw($img);
//$iards->draw($img);
//$iards_label->draw($img);
$lakes->draw($img);
//$watches->draw($img);
$states->draw($img);
$warnings0_c->draw($img);


mktitle($map, $img, "           10 Mar 2009: Flood Status");
$map->embedLegend($img);
$map->drawLabelCache($img);
//mkl($map, $img);

$url = $img->saveWebImage();

echo "<form method=\"GET\" action=\"adjust.php\">
<input type=\"text\" name=\"d\" value=\"$d\">
<input type=\"submit\"><br />";

echo "<img src=\"$url\">";

//print_r($map->extent);
?>
