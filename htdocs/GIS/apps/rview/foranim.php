<?php

$year = $_GET['year'];
$month = $_GET['month'];
$day = $_GET['day'];
$hour = $_GET['hour'];
$minute = $_GET['minute'];

$gts = mktime($hour, $minute, 0, $month, $day, $year);
$ts = $gts - 5*3600;
$dbts = strftime("%Y-%m-%d %H:%M", $ts);

$png = sprintf("/mesonet/ARCHIVE/data/%s/%s/%s/GIS/uscomp/n0r_%s%s%s%s%s.png", $year, $month, $day, $year, $month, $day, $hour, $minute);

`convert $png /tmp/n0r.tif`;

dl("php_mapscript.so");

include("lib.php");

$map = ms_newMapObj("amosaic2.map");
$map->setextent(-300000, 2900000, 500000, 4100000);
$radar = $map->getlayerbyname("radar");
$radar->set("status", MS_ON);
$radar->set("data", "/tmp/n0r.tif");

$states = $map->getlayerbyname("states");
$states->set("status", MS_ON);

$w0c = $map->getlayerbyname("warnings0_c");
$w0c->set("status", MS_ON);
$w0c->setFilter("(expire > '". $dbts ."' and issue < '". $dbts ."' and gtype = 'C')");

$w0p = $map->getlayerbyname("warnings0_p");
$w0p->set("status", MS_ON);
$w0p->setFilter("( expire > '". $dbts ."' and issue < '". $dbts ."' and gtype = 'P')");

$counties = $map->getlayerbyname("counties");
$counties->set("status", MS_ON);

$img = $map->prepareImage();
$states->draw($img);
$counties->draw($img);
$radar->draw($img);
$w0c->draw($img);
$w0p->draw($img);

$d = date("d F Y h:i A" ,  $ts);

mktitle($map, $img, "                  IEM NEXRAD composite base reflect (Iowa only!) valid: $d");
$map->drawLabelCache($img);
mklogolocal($map, $img);

header("Content-type: image/png");
$img->saveImage('', MS_PNG, 0, 0, -1);
?>
