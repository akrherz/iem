<?php
include("../../config/settings.inc.php");
include("../../include/database.inc.php");
$con = iemdb("postgis");


$sql = "SELECT max(valid) as valid from roads_current";
$rs = pg_query($con, $sql);

$row = pg_fetch_array($rs, 0);
$valid = substr($row["valid"],0,16);



$map = ms_newMapObj('roads.map');
//$map->setProjection("init=epsg:4326");
$map->setProjection("init=epsg:26915");
$map->selectOutputFormat("jpeg");

$map->setextent(122487.560, 4443095.235, 809431.656, 4919662.500);
$map->set("width", 720);
$map->set("height", 496);


$img = $map->prepareImage();

$background = $map->getlayerbyname("kwwlback");
$background->set("status", MS_ON);
$background->set("data", "images/26915/kcau.tif");
$background->draw($img);

//$counties = $map->getlayerbyname("counties");
//$counties->set("status", MS_ON);
//$counties->draw($img);

//$states = $map->getlayerbyname("states");
//$states->set("status", MS_ON);
//$states->draw($img);

$roads = $map->getlayerbyname("roads");

$roads->set("status", MS_ON);

if (isset($_GET["extreme"]) )
$roads->set("data", "geom from (select b.type as rtype, b.int1, random() as boid, b.segid, c.cond_code, b.geom from roads_base b, roads_2007_log c WHERE b.segid = c.segid and c.valid = '2007-03-02 00:11' and b.type > 1  ORDER by b.segid DESC) as foo using UNIQUE boid using SRID=26915");

for ($k=0;$k<17;$k++)
{
  $r_c1 = $roads->getClass($k);
  $r_s1 = $r_c1->getStyle(0);
  $r_s1->set("size", 0);

  $r_s1 = $r_c1->getStyle(1);
  $r_s1->set("size", 5);
  if ($k == 0){ $r_s1->color->setRGB(128,128,128); }
}
$roads->draw($img);

$roads_int = $map->getlayerbyname("roads-inter");
$roads_int->set("status", MS_ON);
if (isset($_GET["extreme"]))
$roads_int->set("data", "geom from (select b.type as rtype, b.int1, random() as boid, b.segid, c.cond_code, b.geom from roads_base b, roads_2007_log c WHERE b.segid = c.segid and c.valid = '2007-03-02 00:11' and b.type = 1 and b.us1 NOT IN (6) ORDER by b.segid DESC) as foo using UNIQUE boid using SRID=26915");
for ($k=0;$k<17;$k++)
{
  $r_c1 = $roads_int->getClass($k);
  $r_s1 = $r_c1->getStyle(0);
  $r_s1->set("size", 0);
  $r_s1 = $r_c1->getStyle(1);
  $r_s1->set("size", 7);
  if ($k == 0){ $r_s1->color->setRGB(128,128,128); }
}
$roads_int->draw($img);



$map->drawLabelCache($img);

$layer = $map->getLayerByName("credits");
$c = $layer->getClass(0);
$point = ms_newpointobj();
$point->setXY(500, 10);
$point->draw($map, $layer, $img, 0, $valid);

header("Content-type: image/jpeg");
$img->saveImage('');
?>
