<?php
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$con = iemdb("postgis");

$eightbit = isset($_GET["8bit"]);
$metroview = isset($_GET["metro"]);

$sql = "SELECT max(valid) as valid from roads_current";
$rs = pg_query($con, $sql);

$row = pg_fetch_array($rs, 0);
$valid = substr($row["valid"],0,16);

dl($mapscript);

$map = ms_newMapObj("roads.map");
if ($eightbit)
{
 $map->selectOutputFormat("png");
} else 
{
 $map->selectOutputFormat("png24");
}

$map->setextent(200000,4440000,710000,4940000);
if ($metroview)
{
  $map->setextent(376000,4560000,535000,4680000);
}
$map->set("width", 640);
$map->set("height", 496);


$img = $map->prepareImage();

if (! $eightbit)
{
  $background = $map->getlayerbyname("kcciback");
  if ($metroview)
  {
    $background = $map->getlayerbyname("dsmback");
  }
  $background->set("status", MS_ON);
  $background->draw($img);
}


$counties = $map->getlayerbyname("counties");
if ($metroview)
{
  $counties->draw($img);
}

$states = $map->getlayerbyname("states");
$states->draw($img);

$visibility = $map->getlayerbyname("visibility");
$visibility->draw($img);

$roads = $map->getlayerbyname("roads");
$roads->draw($img);

$roads_int = $map->getlayerbyname("roads-inter");
$roads_int->draw($img);

//$roads_lbl = $map->getlayerbyname("roads_label");
//$roads_lbl->draw($img);
//$roads_lbl->set("connection", $_DATABASE);

$iemlogo = $map->getlayerbyname("iemlogo");
if ($eightbit)
{
  $c2 = $iemlogo->getClass(0);
  $s2 = $c2->getStyle(0);
  $s2->set("symbolname", "iem_isp-8bit");
}
if (! $metroview)
{
  $iemlogo->draw($img);
}

$ia511 = $map->getlayerbyname("ia511");
if ($eightbit)
{
  $c0 = $ia511->getClass(0);
  $s0 = $c0->getStyle(0);
  $s0->set("symbolname", "ia511-8bit");
}

if (! $metroview)
{
  //$ia511->draw($img);
  $pt = ms_newPointObj();
  $pt->setXY(555, 160);
  $pt->draw($map, $ia511, $img, 0, "");
  $pt->free();
}

$logokey2 = $map->getlayerbyname("colorkey");
$c1 = $logokey2->getClass(0);
$s1 = $c1->getStyle(0);
if ($eightbit)
{
  $s1->set("symbolname", "logokey-8bit");
  $s1->set("size", 60);
} else{
  $s1->set("size", 50);
}


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

$logokey2->draw($img);

$layer = $map->getLayerByName("credits");
$c = $layer->getClass(0);
$point = ms_newpointobj();
$point->setXY(500, 10);
$point->draw($map, $layer, $img, "credits", $valid);
$point->free();

$point = ms_newpointobj();
$point->setXY(500, 20);
$point->draw($map, $layer, $img, 1, "Limited Visibility");
$point->free();


header("Content-type: image/png");
$img->saveImage('');
?>
