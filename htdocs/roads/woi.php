<?php
include("../../config/settings.inc.php");
include("../../include/database.inc.php");
$con = iemdb("postgis");

$metroview = isset($_GET["metro"]);

$sql = "SELECT max(valid) as valid from roads_current";
$rs = pg_query($con, $sql);

$row = pg_fetch_array($rs, 0);
$valid = substr($row["valid"],0,16);




$map = ms_newMapObj('roads.map');
$map->imagecolor->setRGB(-1,-1,-1);

//$map->setProjection("init=epsg:4326");
$map->setProjection("init=epsg:26915");
$map->selectOutputFormat("png24");
$map->outputformat->set('imagemode',MS_IMAGEMODE_RGBA);
$map->outputformat->set('transparent',MS_ON);
$map->setSize(1280, 720);
if ($metroview)
{
	$s = 0;
  $map->setextent(307383 -$s, 4543637 -$s, 606903 +$s, 4712117 +$s);
  //$map->setextent(-95.3,  40.71, -92.3,  43.11);
} else
{
  $map->setextent(23650, 4414952, 919650, 4918952);
  //$map->setextent(-107.9, 40, -88.9,  44.9);
}



$img = $map->prepareImage();

if ($metroview)
{
  $background = $map->getlayerbyname("woi-metro");
} else
{
  $background = $map->getlayerbyname("woi-iowa");
}
$background->set("status", MS_OFF);
$background->draw($img);

/*
$counties = $map->getlayerbyname("counties");
$counties->set("status", MS_ON);
$counties->draw($img);
*/

$states = $map->getlayerbyname("states");
$states->set("status", MS_ON);
//$states->draw($img);

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
$img->saveImage('', $map);
?>
