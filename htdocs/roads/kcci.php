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

$map = ms_newMapObj('roads.map');
$map->set("width", 720);
$map->set("height", 496);
if ($eightbit)
{
 $map->selectOutputFormat("png");
} else 
{
 $map->selectOutputFormat("png24");
}


$map->setextent(93926,4393091,813598,4963575);

if ($metroview)
{
  $map->setextent(351000,4556000,551000,4690000);
}
$map->set("width", 720);
$map->set("height", 496);


$img = $map->prepareImage();

if (! $eightbit)
{
  $background = $map->getlayerbyname("kcciback");
  if ($metroview)
  {
    $background->set("data", "images/26915/kccidsm.tif");
  }
  $background->set("status", MS_ON);
  $background->draw($img);
}


$counties = $map->getlayerbyname("counties");
$counties_c1 = $counties->getClass(0);
$counties_s1 = $counties_c1->getStyle(0);
$counties_s1->set("size", 3);
if ($metroview)
{
  //$counties->draw($img);
}

$states = $map->getlayerbyname("states");
$states_c1 = $states->getClass(0);
$states_s1 = $states_c1->getStyle(0);
$states_s1->set("size", 4);
//$states_s1->set("antialias", MS_ON);
if ($eightbit)
{
  $states->draw($img);
}
$roads = $map->getlayerbyname("roads");
if (! $metroview && ! $eightbit)
{
  $roads->set("data", "geom from (select b.type as rtype, b.int1, b.oid as boid, b.segid, c.cond_code, b.geom from roads_base b, roads_current c WHERE b.segid = c.segid and (b.type = 1 or b.us1 IN (18, 20, 30, 34, 71, 63) ) ORDER by b.segid DESC) as foo using UNIQUE boid using SRID=26915");
} else
{
  $roads->set("data", "geom from (select b.type as rtype, b.int1, b.oid as boid, b.segid, c.cond_code, b.geom from roads_base b, roads_current c WHERE b.segid = c.segid and b.type > 1 and b.us1 NOT IN (6) ORDER by b.segid DESC) as foo using UNIQUE boid using SRID=26915");
}
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
if ($eightbit)
{
  $c2 = $iemlogo->getClass(0);
  $s2 = $c2->getStyle(0);
  $s2->set("symbolname", "iem_isp-8bit");
}
if (! $metroview)
{
  //$iemlogo->draw($img);
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
  //$pt->draw($map, $ia511, $img, 0, "");
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

//$logokey2->draw($img);

$layer = $map->getLayerByName("credits");
$c = $layer->getClass(0);
$point = ms_newpointobj();
$point->setXY(500, 10);
$point->draw($map, $layer, $img, "credits", $valid);

header("Content-type: image/png");
$img->saveImage('');
?>
