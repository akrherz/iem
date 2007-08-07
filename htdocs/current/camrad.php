<?php
/* Generate a radar image with camera locs for some time */
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/snet_locs.php");

$db_ts = strftime("%Y-%m-%d %H:%M", $ts );
$cam_ts = strftime("%Y-%m-%d %H:%M", $radts );

$cdrct = Array();
$sql = "SELECT * from camera_current";
if ($isarchive)
  $sql = "SELECT * from camera_log WHERE valid = '$cam_ts'";

$conn = iemdb("mesosite");
$rs = pg_exec($conn, $sql);
for( $i=0; $row = @pg_fetch_array($rs,$i); $i++) 
{  $cdrct[ $row["cam"] ] = $row["drct"]; }


dl($mapscript);

$map = ms_newMapObj("$rootpath/data/gis/base4326.map");
$map->setExtent(-95.0,40.45,-92.1,43.3);
$map->set("width", 320);
$map->set("height", 240);

$namer = $map->getlayerbyname("namerica");
$namer->set("status", 1);

$stlayer = $map->getlayerbyname("states");
$stlayer->set("status", 1);

$counties = $map->getlayerbyname("iacounties");
$counties->set("status", 1);

$c0 = $map->getlayerbyname("warnings0_c");
$c0->set("connection", $_DATABASES["postgis"] );
$c0->set("status", MS_ON );
if ($isarchive)
{
   $c0->set("data", "geom from (select significance, phenomena, geom, oid from warnings_$year WHERE expire > '$db_ts' and issue <= '$db_ts' and gtype = 'C' ORDER by phenomena ASC) as foo using unique oid using SRID=4326");
}else {
   $sql = "geom from (select significance, phenomena, geom, oid from warnings WHERE expire > '$db_ts' and gtype = 'C' ORDER by phenomena ASC) as foo using unique oid using SRID=4326";
   $c0->set("data", $sql);
}

$radar = $map->getlayerbyname("nexrad_n0r");
$radar->set("status", MS_ON );
if ($isarchive) 
{
  $fp = "/mesonet/ARCHIVE/data/". gmdate('Y/m/d/', $radts) ."GIS/uscomp/n0r_". gmdate('YmdHi', $radts) .".png";
  if (! is_file($fp))
    echo "<br /><i><b>NEXRAD composite not available: $fp</b></i>";
  $radfile = $fp;
  $radar->set("data", $radfile);
}


$cp = ms_newLayerObj($map);
$cp->set("type", MS_SHAPE_POINT);
$cp->set("status", MS_ON);
$cp->set("labelcache", MS_OFF);
$cl = ms_newClassObj($cp);
$cl->label->set("type", MS_BITMAP);
$cl->label->set("size", MS_MEDIUM);
$cl->label->set("position", MS_CR);
$cl->label->set("force", MS_ON);
$cl->label->set("offsetx", 6);
$cl->label->set("offsety", 0);
$cl->label->outlinecolor->setRGB(255, 255, 255);

$cl2 = ms_newClassObj($cp);
$cl2->label->set("type", MS_TRUETYPE);
$cl2->label->set("size", "10");
$cl2->label->set("font", "esri34");
$cl2->label->set("position", MS_CC);
$cl2->label->set("force", MS_ON);
$cl2->label->set("partials", MS_ON);
$cl2->label->outlinecolor->setRGB(0, 0, 0);
$cl2->label->color->setRGB(255, 255, 255);

//$sl = ms_newStyleObj($cl);
//$sl->set("symbolname", "arrow");
//$sl->set("size", 8);
//$sl->color->setRGB(255, 255, 255);
//$sl = ms_newStyleObj($cl);
//$sl->set("symbolname", "circle");
//$sl->set("size", 6);
//$sl->color->setRGB(0, 0, 0);


$img = $map->prepareImage();
$namer->draw($img);
$counties->draw($img);
$stlayer->draw( $img);
$radar->draw($img);
$c0->draw($img);

/* Draw Points */
reset($cameras);
while (list($key, $val) = each($cameras))
{
   if (! $cameras[$key]["active"]) continue;
   $pt = ms_newPointObj();
   $pt->setXY($cities["KCCI"][$key]["lon"], $cities["KCCI"][$key]["lat"], 0);
   $pt->draw($map, $cp, $img, 0, $cameras[$key]['num'] );
   $pt->free();

   $pt = ms_newPointObj();
   $pt->setXY($cities["KCCI"][$key]["lon"], $cities["KCCI"][$key]["lat"], 0);
   $cl2->label->set("angle",  (0 - $cdrct[$key]) + 90 );
   $pt->draw($map, $cp, $img, 1, 'a' );
   $pt->free();

}
$d = date("m/d/Y h:i A", $radts);

$layer = $map->getLayerByName("credits");
$point = ms_newpointobj();
$point->setXY(125, 10);
$point->draw($map, $layer, $img, "credits",  "RADAR: $d");

$map->drawLabelCache($img);

$url = $img->saveWebImage();

echo "<div style=\"float: left;\"><b>Radar View:</b><br /><img src=\"$url\"></div>";
?>
