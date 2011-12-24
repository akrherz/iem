<?php
include("../../../../config/settings.inc.php");
include_once "$rootpath/include/iemmap.php";
//  mesoplot/plot.php
//  - Replace GEMPAK mesoplots!!!
$i = isset($_GET["i"]) ? $_GET["i"] : "1h";

$now = time();
$plotts = $now;
if ($i == "1h")
{
	$plotts = mktime( date("H"), 10, 0, date("m"), date("d"), date("Y") );
	if ( date("i", $now) < 10 ){
		$plotts -= 3600;
	}
}

$map = ms_newMapObj("$rootpath/data/gis/base4326.map");
$map->setExtent(-96.7, 39.65, -90, 44.42);


$counties = $map->getlayerbyname("uscounties");
$counties->set("status", MS_ON);

$states = $map->getlayerbyname("states");
$states->set("status", MS_ON);

if ($i == "1h")
	$temps = $map->getlayerbyname("delta-surface");
else
	$temps = $map->getlayerbyname("delta-surface15m");
$temps->set("status", MS_ON);

$n0r = $map->getlayerbyname("nexrad_n0q");
$n0r->set("status", MS_ON);

$img = $map->prepareImage();
$namer = $map->getlayerbyname("namerica");
$namer->set("status", MS_ON);
$namer->draw($img);

$n0r->draw($img);
$counties->draw($img);
$states->draw($img);
$temps->draw($img);
$t = date("d M Y h:i A", $plotts);
if ($i == "1h")
iemmap_title($map, $img, "1 hour Pressure Change [inches]"," valid $t");
if ($i == "15m")
iemmap_title($map, $img, "Recent 15 minute Pressure Change [inches]"," valid $t");
$map->drawLabelCache($img);

header("Content-type: image/png");
$img->saveImage('');
?>
