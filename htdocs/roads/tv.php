<?php
require_once "/usr/lib64/php/modules/mapscript.php";

require_once "../../config/settings.inc.php";
require_once "../../include/database.inc.php";
$con = iemdb("postgis");

// kvillewxguy@hotmail.com
$metroview = isset($_GET["metro"]);

$sql = "SELECT max(valid) as valid from roads_current";
$rs = pg_query($con, $sql);

$row = pg_fetch_array($rs, 0);
$valid = substr($row["valid"], 0, 16);

$map = new MapObj('roads.map');
//$map->setProjection("init=epsg:4326");
$map->setProjection("init=epsg:26915");
$map->selectOutputFormat("png24");

if ($metroview) {
    $map->setextent(360000, 4580000, 559000, 4690000);
    //$map->setextent(-95.3,  40.71, -92.3,  43.11);
} else {
    $map->setextent(190000, 4430000, 759000, 4910000);
    //$map->setextent(-107.9, 40, -88.9,  44.9);
}
$map->setsize(720, 496);


$img = $map->prepareImage();

$states = $map->getLayerByName("states");
$states->__set("status", MS_ON);
$states->draw($map, $img);

$roads = $map->getLayerByName("roads");
$roads->__set("status", MS_ON);

for ($k = 0; $k < 17; $k++) {
    $r_c1 = $roads->getClass($k);
    $r_s1 = $r_c1->getStyle(0);
    $r_s1->__set("size", 0);
    $r_s1 = $r_c1->getStyle(1);
    $r_s1->__set("size", 5);
}
$roads->draw($map, $img);

$roads_int = $map->getLayerByName("roads-inter");
$roads_int->__set("status", MS_ON);
for ($k = 0; $k < 17; $k++) {
    $r_c1 = $roads_int->getClass($k);
    $r_s1 = $r_c1->getStyle(0);
    $r_s1->__set("size", 0);
    $r_s1 = $r_c1->getStyle(1);
    $r_s1->__set("size", 7);
}
$roads_int->draw($map, $img);

$map->drawLabelCache($img);

header("Content-type: image/png");
echo $img->getBytes();
