<?php
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$con = iemdb("postgis");


// kvillewxguy@hotmail.com
$metroview = isset($_GET["metro"]);

$sql = "SELECT max(valid) as valid from roads_current";
$rs = pg_query($con, $sql);

$row = pg_fetch_array($rs, 0);
$valid = substr($row["valid"],0,16);

//$mapscript = "php_mapscript_cvs.so";
dl($mapscript);

$map = ms_newMapObj('roads.map');
//$map->setProjection("init=epsg:4326");
$map->setProjection("init=epsg:26915");
$map->selectOutputFormat("png24");

if ($metroview)
{
  $map->setextent(360000, 4580000, 559000, 4690000);
  //$map->setextent(-95.3,  40.71, -92.3,  43.11);
} else
{
  $map->setextent(190000, 4430000, 759000, 4910000);
  //$map->setextent(-107.9, 40, -88.9,  44.9);
}
$map->set("width", 720);
$map->set("height", 496);


$img = $map->prepareImage();

if ($metroview)
{
  $background = $map->getlayerbyname("woiback");
} else
{
  $background = $map->getlayerbyname("ia_woiback");
}
$background->set("status", MS_ON);
$background->draw($img);

/*
$counties = $map->getlayerbyname("counties");
$counties->set("status", MS_ON);
$counties->draw($img);
*/

$states = $map->getlayerbyname("states");
$states->set("status", MS_ON);
$states->draw($img);

$roads = $map->getlayerbyname("roads");
$roads->set("transparency", MS_GD_ALPHA);
for ($k=0;$k<17;$k++)
{
  $r_c1 = $roads->getClass($k);
  $r_s1 = $r_c1->getStyle(0);
  $r_s1->set("size", 0);
  $r_s1 = $r_c1->getStyle(1);
  $r_s1->set("size", 5);
}
$roads->draw($img);

$roads_int = $map->getlayerbyname("roads-inter");
for ($k=0;$k<17;$k++)
{
  $r_c1 = $roads_int->getClass($k);
  $r_s1 = $r_c1->getStyle(0);
  $r_s1->set("size", 0);
  $r_s1 = $r_c1->getStyle(1);
  $r_s1->set("size", 7);
}
$roads_int->draw($img);

/*
$roads_lbl = $map->getlayerbyname("roads_label");
if (! $metroview)
{
 $c1 = $roads_lbl->getClass(1);
 $c1->set("maxscale", 25);
 $c2 = $roads_lbl->getClass(2);
 $c2->set("maxscale", 25);
}

$roads_lbl->draw($img);
*/

//$cities = $map->getlayerbyname("cities");
//$cities->set("status", MS_ON);
//$cities->draw($img);

/*
$logokey = ms_newLayerObj($map);
$logokey->set("type", MS_SHAPE_POINT);
$logokey->set("transform", MS_FALSE);
$logokey->set("status", MS_ON);
$logokey->set("labelcache", MS_ON);

$logokey_c0 = ms_newClassObj($logokey);
$logokey_c0s0 = ms_newStyleObj($logokey_c0);
$logokey_c0s0->set("symbolname", "logokey");
$logokey_c0s0->set("size", 45);
$logokey_c0s0->color->setRGB(0,0,0);
$logokey_c0->label->set("buffer", 20);
$logokey_c0->label->set("type", MS_BITMAP);
$logokey_c0->label->set("size", MS_GIANT);
$logokey_c0->label->color->setRGB(0,0,0);
$logopt = ms_newpointobj();
$logopt->setXY(319, 440);
$logopt->draw($map, $logokey, $img, 0, "            ");
$logopt->free();

$logokey_c1 = ms_newClassObj($logokey);
$logokey_c1s0 = ms_newStyleObj($logokey_c1);
$logokey_c1s0->set("symbolname", "ia511");
$logokey_c1s0->set("size", 45);
$logokey_c1->label->set("buffer", 20);
$logokey_c1->label->set("type", MS_BITMAP);
$logokey_c1->label->set("size", MS_GIANT);
$logokey_c1->label->color->setRGB(0,0,0);
$ia511pt = ms_newpointobj();
$ia511pt->setXY(575, 440);
$ia511pt->draw($map, $logokey, $img, 1, "              ");

$logokey_c2 = ms_newClassObj($logokey);
$logokey_c2s0 = ms_newStyleObj($logokey_c2);
$logokey_c2s0->set("symbolname", "iem");
$logokey_c2s0->set("size", 45);
$logokey_c2->label->set("buffer", 20);
$logokey_c2->label->set("type", MS_BITMAP);
$logokey_c2->label->set("size", MS_GIANT);
$logokey_c2->label->color->setRGB(0,0,0);
$iempt = ms_newpointobj();
$iempt->setXY(59, 440);
$iempt->draw($map, $logokey, $img, 2 , "                ");

if (! $metroview)
{
 $logokey_c3 = ms_newClassObj($logokey);
 $logokey_c3s0 = ms_newStyleObj($logokey_c3);
 //$logokey_c3s0->set("symbolname", "iem");
 $logokey_c3s0->set("size", 45);
 $logokey_c3->label->set("buffer", 2);
 $logokey_c3->label->set("type", MS_BITMAP);
 $logokey_c3->label->set("size", MS_MEDIUM);
 $logokey_c3->label->color->setRGB(0,0,0);
 $bpt = ms_newpointobj();
 $bpt->setXY(320, 300);
 $bpt->draw($map, $logokey, $img, 3 , "");
}

*/
$map->drawLabelCache($img);
/*
$layer = $map->getLayerByName("credits");
$c = $layer->getClass(0);
$point = ms_newpointobj();
$point->setXY(500, 10);
$point->draw($map, $layer, $img, "credits", $valid);
*/

header("Content-type: image/png");
$img->saveImage('');
?>
