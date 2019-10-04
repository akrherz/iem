<?php
/*
 * Custom Road display for WHO-TV
 */
include("../../config/settings.inc.php");
include("../../include/database.inc.php");

$isnew = isset($_REQUEST["new"]);

$con = iemdb("postgis");


$sql = "SELECT max(valid) as valid from roads_current";
$rs = pg_query($con, $sql);

$row = pg_fetch_array($rs, 0);
$valid = substr($row["valid"],0,16);



$map = ms_newMapObj('roads.map');
//$map->setProjection("init=epsg:4326");
$map->setProjection("init=epsg:26915");
$map->selectOutputFormat("jpeg");

if ($isnew){
	$map->setSize(1920,1080);
	$map->setextent(26254, 4429290, 894647, 4917732);
} else{
	$map->setextent(117487.560, 4448095.235, 795431.656, 4919662.500);
	$map->setSize(1280,720);
}

$img = $map->prepareImage();

$background = $map->getlayerbyname("kwwlback");
$background->set("status", MS_ON);
if ($isnew){
	$background->set("data", "images/26915/who-new.png");
} else {
	$background->set("data", "images/26915/who.tif");
}
$background->draw($img);

//$counties = $map->getlayerbyname("counties");
//$counties->set("status", MS_ON);
//$counties->draw($img);

//$states = $map->getlayerbyname("states");
//$states->set("status", MS_ON);
//$states->draw($img);

$roads = $map->getlayerbyname("roads");
$roads->set("status", MS_ON);
if ($isnew){
	$roads->setFilter('([rtype] < 3 or [st1] = 163)');
}
for ($k=0;$k<17;$k++)
{
  $r_c1 = $roads->getClass($k);
  $r_s1 = $r_c1->getStyle(0);
  $r_s1->set("width", 0);

  $r_s1 = $r_c1->getStyle(1);
  $r_s1->set("width", 5);
  if ($k == 0){ $r_s1->color->setRGB(0,0,0); }
}
$roads->draw($img);

$roads_int = $map->getlayerbyname("roads-inter");
$roads_int->set("status", MS_ON);
if (isset($_GET["extreme"]))
$roads_int->set("data", "geom from (select b.us1, b.type as rtype, b.int1, random() as boid, b.segid, c.cond_code, b.geom from roads_base b, roads_2007_log c WHERE b.segid = c.segid and c.valid = '2007-03-02 00:11' and b.type = 1 and b.us1 NOT IN (6) ORDER by b.segid DESC) as foo using UNIQUE boid using SRID=26915");
for ($k=0;$k<17;$k++)
{
  $r_c1 = $roads_int->getClass($k);
  $r_s1 = $r_c1->getStyle(0);
  $r_s1->set("width", 0);
  $r_s1 = $r_c1->getStyle(1);
  $r_s1->set("width", 7);
  if ($k == 0){ $r_s1->color->setRGB(0,0,0); }
}
$roads_int->draw($img);


$map->drawLabelCache($img);

$layer = $map->getLayerByName("credits");
$c = $layer->getClass(0);
$point = ms_newpointobj();
$point->setXY(1150, 10);
$point->draw($map, $layer, $img, 0, $valid);
$map->drawLabelCache($img);

header("Content-type: image/jpeg");
$img->saveImage('');
?>
