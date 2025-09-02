<?php
/* Generate a plot of a locations RADAR by year */
require_once "../../config/settings.inc.php";
require_once "../../include/vendor/mapscript.php";
require_once "../../include/forms.php";

$mapFile = "../../data/gis/base4326.map";

$beginYear = 1995;
$endYear = intval(date("Y"));

$twidth = 160 - 2;
$theight = 140 - 2;
$header = 40;
$cols = 6;

$ts = time();
$m = intval(date("i", $ts));
$ts = $ts - (($m % 5) * 60.0);

$day = get_int404("day", date("d", $ts));
$month = get_int404("month", date("m", $ts));
$year = get_int404("year", date("Y", $ts));
$hour = get_int404("hour", date("H", $ts));
$minute = get_int404("minute", date("i", $ts));
$extents = isset($_GET["BBOX"]) ? explode(",", $_GET["BBOX"]) : array(-105, 40, -97, 47);
$dt = new DateTime("{$year}-{$month}-{$day} {$hour}:{$minute}");

/* This is our final image!  */
$map2 = new mapObj($mapFile);
$map2->imagecolor->setrgb(155, 155, 155);
$map2->setSize($twidth * $cols + 11, $theight * 6 + $header + 13);
$img2 = $map2->prepareImage();

/* Title Bar */
$bar640t = $map2->getLayerByName("bar640t");
$bar640t->__set("status", MS_ON);
$bar640t->draw($map2, $img2);

/* Draw the title */
$tlayer = $map2->getLayerByName("bar640t-title");
$point = new pointObj();
$point->setXY(80, 16);
$d = $dt->format("d M h:i A");
$point->draw($map2, $tlayer, $img2, 0, "NEXRAD by Year for Time: $d");

/* Draw the subtitle */
$point = new pointObj();
$point->setXY(80, 31);
$d = date("d M Y h:i A T");
$point->draw($map2, $tlayer, $img2, 1, " map generated $d");

/* Draw the logo! */
$layer = $map2->getLayerByName("logo");
$c0 = $layer->getClass(0);
$c0s0 = $c0->getStyle(0);
$c0s0->__set("size", 40);
$point = new pointObj();
$point->setXY(40, 20);
$point->draw($map2, $layer, $img2, 0, "");

$layer = $map2->getLayerByName("n0r-ramp");
$point = new pointObj();
$point->setXY(560, 15);
$point->draw($map2, $layer, $img2, 0, "");

$map2->drawLabelCache($img2);

$gdimg_dest = imagecreatefromstring($img2->getBytes());

$i = 0;
$utcnow = new DateTime('now', new DateTimeZone("UTC"));
for ($year = $beginYear; $year <= $endYear; $year++) {
    $radts = new DateTime("{$year}-{$month}-{$day} {$hour}:{$minute}");
    $radts->setTimezone(new DateTimeZone("UTC"));
    if ($radts > $utcnow) {
        continue;
    }

    /* Render the little maps */
    $map = new mapObj($mapFile);
    $map->__set("width", $twidth);
    $map->__set("height", $theight);
    $map->setExtent($extents[0], $extents[1], $extents[2], $extents[3]);

    $img = $map->prepareImage();

    $namerica = $map->getLayerByName("namerica");
    $namerica->__set("status", MS_ON);
    $namerica->draw($map, $img);

    $lakes = $map->getLayerByName("lakes");
    $lakes->__set("status", MS_ON);
    $lakes->draw($map, $img);

    /* Draw NEXRAD Layer */
    $radarfp =  sprintf(
        "/mesonet/ARCHIVE/data/%s/GIS/uscomp/n0r_%s.png",
        $radts->format("Y/m/d"),
        $radts->format("YmdHi"),
    );
    if (is_file($radarfp)) {
        $radar = $map->getLayerByName("nexrad_n0r");
        $radar->__set("status", MS_ON);
        $radar->__set("data", $radarfp);
        $radar->draw($map, $img);
    }

    $counties = $map->getLayerByName("uscounties");
    if (($extents[2] - $extents[0]) > 5) {
        $counties->__set("status", MS_OFF);
    } else {
        $counties->__set("status", MS_ON);
    }
    $counties->draw($map, $img);

    $states = $map->getLayerByName("states");
    $states->__set("status", MS_ON);
    $states->draw($map, $img);

    $bar640t = $map->getLayerByName("bar640t");
    $bar640t->__set("status", 1);

    $tlayer = $map->getLayerByName("bar640t-title");
    $point = new pointObj();
    $point->setXY(2, 12);
    $point->draw($map, $tlayer, $img, 1, "$year");

    $map->drawLabelCache($img);

    $y0 = intval($i / $cols) * ($theight + 3)  + $header;
    $x0 = ($i % $cols) * ($twidth + 3)  + 3;
    $gdimg_src = imagecreatefromstring($img->getBytes());
    imagecopy(
        $gdimg_dest,
        $gdimg_src,
        $x0,
        $y0,
        0, 0, $twidth, $theight,
    );
    imagedestroy($gdimg_src);
    $i += 1;
}
header("Content-type: image/png");
echo imagepng($gdimg_dest);
