<?php
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$con = iemdb("postgis");



$metroview = isset($_GET["iowa"]);

$sql = "SELECT max(valid) as valid from roads_current";
$rs = pg_query($con, $sql);

$row = pg_fetch_array($rs, 0);
$valid = substr($row["valid"],0,16);

dl($mapscript);

$map = ms_newMapObj('roads.map');
$map->set("width", 720);
$map->set("height", 486);
$map->selectOutputFormat("png24");


$map->setextent(278059.446, 4477454.931, 850841.343, 4894440.667);


if ($metroview)
{
  $map->setProjection("init=epsg:4326");
  $map->setextent(-97.2008500, 40.5280900, -89.4568500,  44.1338900);
}
$map->set("width", 720);
$map->set("height", 486);

$img = $map->prepareImage();

$background = $map->getlayerbyname("kcrg-dma");
if ($metroview)
{
  $background = $map->getlayerbyname("kcrg-iowa");
}
$background->set("status", MS_ON);
$background->draw($img);


$roads = $map->getlayerbyname("roads");
$roads->set("status", MS_ON);
$roads->set("transparency", MS_GD_ALPHA);
for ($k=0;$k<17;$k++)
{
  $r_c1 = $roads->getClass($k);
  $r_s1 = $r_c1->getStyle(0);
  $r_s1->set("size", 0);
  $r_s1 = $r_c1->getStyle(1);
  $r_s1->set("size", 5);
  //$r_s1->set("antialias", MS_ON);
}
$roads->draw($img);

$roads_int = $map->getlayerbyname("roads-inter");
$roads_int->set("status", MS_ON);
for ($k=0;$k<17;$k++)
{
  $r_c1 = $roads_int->getClass($k);
  $r_s1 = $r_c1->getStyle(0);
  $r_s1->set("size", 0);
  $r_s1 = $r_c1->getStyle(1);
  $r_s1->set("size", 7);
}
$roads_int->draw($img);


$iemlogo = $map->getlayerbyname("iemlogo");
$c2 = $iemlogo->getClass(0);
$s2 = $c2->getStyle(0);
$s2->set("symbolname", "iem_isp-8bit");
if (! $metroview)
{
  //$iemlogo->draw($img);
}

$ia511 = $map->getlayerbyname("ia511");
  $c0 = $ia511->getClass(0);
  $s0 = $c0->getStyle(0);
  $s0->set("symbolname", "ia511-8bit");

if (! $metroview)
{
  //$ia511->draw($img);
  $pt = ms_newPointObj();
  $pt->setXY(555, 160);
  //$pt->draw($map, $ia511, $img, 0, "");
  $pt->free();
}

$logokey2 = $map->getlayerbyname("colorkey");
$c1 = $logokey2->getClass(0);
$s1 = $c1->getStyle(0);
  $s1->set("symbolname", "logokey-8bit");
  $s1->set("size", 60);


$logokey = ms_newLayerObj($map);
$logokey->set("type", MS_SHP_POINT);
$logokey->set("transform", MS_FALSE);
$logokey->set("status", MS_ON);
$logokey->set("labelcache", MS_ON);


$logokey_c3 = ms_newClassObj($logokey);
$logokey_c3s0 = ms_newStyleObj($logokey_c3);
//$logokey_c3s0->set("symbolname", "iem");
//$logokey_c3s0->set("size", 45);
$logokey_c3->label->set("buffer", 10);
$logokey_c3->label->set("type", MS_BITMAP);
$logokey_c3->label->set("size", MS_MEDIUM);
$logokey_c3->label->color->setRGB(0,0,0);
$bpt = ms_newpointobj();
$bpt->setXY(300, 300);
$bpt->draw($map, $logokey, $img, 0 , "      ");

$map->drawLabelCache($img);

//$logokey2->draw($img);

$layer = $map->getLayerByName("credits");
$c = $layer->getClass(0);
$point = ms_newpointobj();
$point->setXY(500, 10);
$point->draw($map, $layer, $img, "credits", $valid);

header("Content-type: image/png");
$img->saveImage('');
?>
