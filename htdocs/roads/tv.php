<?php
include("../../config/settings.inc.php");
include("../../include/database.inc.php");
$con = iemdb("postgis");


// kvillewxguy@hotmail.com
$metroview = isset($_GET["metro"]);

$sql = "SELECT max(valid) as valid from roads_current";
$rs = pg_query($con, $sql);

$row = pg_fetch_array($rs, 0);
$valid = substr($row["valid"],0,16);




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
$map->setsize(720, 496);


$img = $map->prepareImage();

/*
if ($metroview)
{
  $background = $map->getlayerbyname("woiback");
} else
{
  $background = $map->getlayerbyname("ia_woiback");
}
$background->set("status", MS_ON);
$background->draw($img);
*/

/*
$counties = $map->getlayerbyname("counties");
$counties->set("status", MS_ON);
$counties->draw($img);
*/

$states = $map->getlayerbyname("states");
$states->set("status", MS_ON);
$states->draw($img);

$roads = $map->getlayerbyname("roads");
$roads->set("status", MS_ON);

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

$map->drawLabelCache($img);


header("Content-type: image/png");
$img->saveImage('');
?>
