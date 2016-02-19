<?php
include("../../config/settings.inc.php");
include("../../include/database.inc.php");
$con = iemdb("postgis");

$eightbit = isset($_GET["8bit"]);

$sql = "SELECT max(valid) as valid from roads_current";
$rs = pg_query($con, $sql);

$row = pg_fetch_array($rs, 0);
$valid = substr($row["valid"],0,16);

$map = ms_newMapObj('roads.map');
$map->setSize(1920, 1080);
//$map->set('units', MS_DD);
//$map->setProjection("init=epsg:4326");
//$map->setExtent(-98.973, 40., -87.84, 44.8);
$map->setExtent(-9300, 4438266, 940009, 4977246);
$map->selectOutputFormat("png24");
$img = $map->prepareImage();


$background = $map->getlayerbyname("ktivback");
$background->set("status", MS_ON);
$background->draw($img);

//$counties = $map->getlayerbyname("counties");
//$counties->set('status', MS_ON);
//$counties->draw($img);
//$counties_c1 = $counties->getClass(0);
//$counties_s1 = $counties_c1->getStyle(0);
//$counties_s1->set("size", 3);

$roads = $map->getlayerbyname("roads");
$roads->set("status", MS_ON);
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

//$roads_lbl = $map->getlayerbyname("roads_label");
//$roads_lbl->set("status", MS_OFF);
//if ($eightbit)
//{  $roads_lbl->set("status", MS_ON);
//}
//$roads_lbl->draw($img);

$iemlogo = $map->getlayerbyname("iemlogo");
$ia511 = $map->getlayerbyname("ia511");

  $pt = ms_newPointObj();
  $pt->setXY(555, 160);
  //$pt->draw($map, $ia511, $img, 0, "");


$logokey2 = $map->getlayerbyname("colorkey");
$c1 = $logokey2->getClass(0);
$s1 = $c1->getStyle(0);
  $s1->set("size", 50);


$logokey = ms_newLayerObj($map);
$logokey->set("type", MS_SHP_POINT);
$logokey->set("transform", MS_FALSE);
$logokey->set("status", MS_ON);
$logokey->set("labelcache", MS_ON);


$logokey_c3 = ms_newClassObj($logokey);
$logokey_c3s0 = ms_newStyleObj($logokey_c3);
//$logokey_c3s0->set("symbolname", "iem");
//$logokey_c3s0->set("size", 45);
$l = $logokey_c3->addLabel(new labelObj());
$logokey_c3->getLabel(0)->set("buffer", 10);
$logokey_c3->getLabel(0)->set("size", MS_MEDIUM);
$logokey_c3->getLabel(0)->color->setRGB(0,0,0);
$bpt = ms_newpointobj();
$bpt->setXY(300, 300);
$bpt->draw($map, $logokey, $img, 0 , "      ");

$map->drawLabelCache($img);

//$logokey2->draw($img);

$layer = $map->getLayerByName("credits");
$c = $layer->getClass(0);
$point = ms_newpointobj();
$point->setXY(500, 10);
$point->draw($map, $layer, $img, 0, $valid);

header("Content-type: image/png");
$img->saveImage('');
$map->free();
?>
