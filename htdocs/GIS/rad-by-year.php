<?php
/* Generate a plot of a locations RADAR by year */
include("../../config/settings.inc.php");
dl($mapscript);
$mapFile = $rootpath."/data/gis/base4326.map";

$beginYear = 1995;
$endYear = intval( date("Y") );
$yearsPerRow = 4;


$twidth = 160 - 2;
$theight = 140 - 2;
$header = 40;

$ts = time();
$m = intval( date("i", $ts) );
$ts = $ts - (($m % 5) * 60.0);

$day = isset($_GET["day"]) ? intval($_GET["day"]) : date("d", $ts);
$month = isset($_GET["month"]) ? intval($_GET["month"]) : date("m", $ts);
$year = isset($_GET["year"]) ? intval($_GET["year"]) : date("Y", $ts);
$hour = isset($_GET["hour"]) ? intval($_GET["hour"]) : date("H", $ts);
$minute = isset($_GET["minute"]) ? intval($_GET["minute"]) : date("i", $ts);
$extents = isset($_GET["BBOX"]) ? explode(",", $_GET["BBOX"]) : Array(-105,40,-97,47);
$ts = mktime($hour, $minute, 0, $month, $day, $year);

/* This is our final image!  */
$map2 = ms_newMapObj($mapFile);
$map2->imagecolor->setrgb(155,155,155);
$map2->set("width", $twidth * 4 + 11);
$map2->set("height",$theight * 4 + $header + 13);
$img2 = $map2->prepareImage();

/* Title Bar */
$bar640t = $map2->getLayerByName("bar640t");
$bar640t->set("status", 1);
$bar640t->draw($img2);

/* Draw the title */
$tlayer = $map2->getLayerByName("bar640t-title");
$point = ms_newpointobj();
$point->setXY(80, 12);
$d = date("d M h:i A", $ts);
$point->draw($map2, $tlayer, $img2, 0,"NEXRAD by Year for Time: $d");
$point->free();

/* Draw the subtitle */
$point = ms_newpointobj();
$point->setXY(80, 29);
$d = date("d M Y h:i A T");
$point->draw($map2, $tlayer, $img2, 1," map generated $d");
$point->free();

/* Draw the logo! */
$layer = $map2->getLayerByName("logo");
$c0 = $layer->getClass(0);
$c0s0 = $c0->getStyle(0);
$c0s0->set("size", 40);
$point = ms_newpointobj();
$point->setXY(40, 20);
$point->draw($map2, $layer, $img2, "logo", "");
$point->free();

$layer = $map2->getLayerByName("n0r-ramp");
$point = ms_newpointobj();
$point->setXY(560, 15);
$point->draw($map2, $layer, $img2, "n0r-ramp", "");
$point->free();

$map2->drawLabelCache($img2);

$i = 0;
for ($year=$beginYear; $year <= $endYear; $year++)
{
  $radts = mktime($hour,$minute,0,$month,$day,$year);
  if ($radts > time()){ continue; }

  /* Render the little maps */
  $map = ms_newMapObj($mapFile);
  $map->set("width", $twidth);
  $map->set("height",$theight);
  $map->setExtent($extents[0], $extents[1], $extents[2], $extents[3]); 

  $img = $map->prepareImage();

  $namerica = $map->getlayerbyname("namerica");
  $namerica->set("status", MS_ON);
  $namerica->draw($img);

  $lakes = $map->getlayerbyname("lakes");
  $lakes->set("status", MS_ON);
  $lakes->draw($img);

  /* Draw NEXRAD Layer */
  $radar = $map->getlayerbyname("nexrad_n0r");
  $radar->set("status", MS_ON);
  $radar->set("data", gmstrftime("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/uscomp/n0r_%Y%m%d%H%M.png", $radts) );
  $radar->draw($img);

  $counties = $map->getlayerbyname("uscounties");
  if (($extents[2] - $extents[0]) > 5) {
    $counties->set("status", MS_OFF);
  } else {
    $counties->set("status", MS_ON);
  }
  $counties->draw($img);

  $states = $map->getlayerbyname("states");
  $states->set("status", MS_ON);
  $states->draw($img);

  $bar640t = $map->getLayerByName("bar640t");
  $bar640t->set("status", 1);
  //$bar640t->draw($img);

  $tlayer = $map->getLayerByName("bar640t-title");
  $point = ms_newpointobj();
  $point->setXY(2, 8);
  $point->draw($map, $tlayer, $img, 1,"$year");
  $point->free();


  $map->drawLabelCache($img);

  $y0 = intval($i / 4) * ($theight+3) + ($theight/2) + $header;
  $x0 = ($i % 4) * ($twidth+3) + ($twidth/2) + 3;
  $img2->pasteImage($img, -1, $x0, $y0, 0);
  $i += 1;
}
header ("Content-type: image/png");
$img2->saveImage('');
?>
