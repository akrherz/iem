<?php

$year = $_GET['year'];
$month = $_GET['month'];
$day = $_GET['day'];
$hour = $_GET['hour'];
$minute = $_GET['minute'];

$gts = mktime($hour, $minute, 0, $month, $day, $year);
$ts = $gts - 5*3600; // Hack Hack
$dbts = strftime("%Y-%m-%d %H:%M", $ts);

$png = sprintf("/mesonet/ARCHIVE/data/%s/%s/%s/GIS/kcci/KCCI_%s%s%s%s%s.png", $year, $month, $day, $year, $month, $day, $hour, $minute);

`convert $png /tmp/kcci.tif`;

function mklogolocal($map, $imgObj) {
                                                                                
 $layer = $map->getLayerByName("doppler8");
                                                                                
 // point feature with text for location
 $point = ms_newpointobj();
 $point->setXY(144, 34);
                                                                                
 $point->draw($map, $layer, $imgObj, "logo", "");
}

function mktitle($map, $imgObj, $titlet) {
  $layer = $map->getLayerByName("credits");
                                                                                
  // point feature with text for location
  $point = ms_newpointobj();
  $point->setXY(60, 55);
                                                                                
  $point->draw($map, $layer, $imgObj, "credits",
    $titlet);
}

dl("php_mapscript_401.so");


$map = ms_newMapObj("kcci.map");
$map->setextent(355816.248688867, 4516855.8849683,474162.648313359, 4635882.57204873);

$map->set("width", 640);
$map->set("height", 496);
//$map->SelectOutputFormat("jpeg");
$radar = $map->getlayerbyname("radar");
$radar->set("status", MS_ON);
$radar->set("data", "/tmp/kcci.tif");
$radar->setProjection("init=epsg:26915");

$states = $map->getlayerbyname("states");
$states->set("status", MS_ON);

$w0c = $map->getlayerbyname("warnings0_c");
$w0c->set("status", MS_ON);
$w0c->setFilter("(expire > '". $dbts ."' and issue < '". $dbts ."' and gtype = 'C')");

$w0p = $map->getlayerbyname("warnings0_p");
$w0p->set("status", MS_ON);
$w0p->setFilter("( expire > '". $dbts ."' and issue < '". $dbts ."' and gtype = 'P')");

$interstates = $map->getlayerbyname("interstates");
$interstates->set("status", MS_ON);



$counties = $map->getlayerbyname("counties");
$counties->set("status", MS_ON);

$img = $map->prepareImage();
$counties->draw($img);
$states->draw($img);
$radar->draw($img);
$radar->draw($img);
$interstates->draw($img);
//$w0p->draw($img);
$w0c->draw($img);

$d = date("d F Y h:i A" ,  $ts);

mktitle($map, $img, " $d ");
$map->drawLabelCache($img);
mklogolocal($map, $img);

header("Content-type: image/png");
$img->saveImage('', MS_PNG, 0, 0, -1);
?>
