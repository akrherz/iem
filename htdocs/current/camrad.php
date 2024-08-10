<?php
/* 
 * Generate a RADAR image with webcams overlain for some *UTC* timestamp!
 */
require_once "/usr/lib64/php/modules/mapscript.php";
require_once "../../config/settings.inc.php";
require_once "../../include/database.inc.php";
require_once "../../include/cameras.inc.php";
$conn = iemdb("mesosite");

/* First, we need some GET vars */
$network = isset($_GET["network"])
    ? substr($_GET["network"], 0, 4) : die("No \$network Set");
$ts = null;
if ($network == "KCRG") {
    $cameras["KCCI-017"]["network"] = "KCRG";
}

if (isset($_GET["ts"]) && $_GET["ts"] != "0") {
    $ts = DateTime::createFromFormat('YmdHi', $_GET["ts"]);
}

if (! is_null($ts)) {
    // If we are in archive mode and requesting a non 5 minute interval,
    // what shall we do? Lets check for entries in the database
    $sql = sprintf(
        "SELECT * from camera_log WHERE valid = '%s'",
        $ts->format("Y-m-d H:i")
    );
    $rs = pg_exec($conn, $sql);
    if (pg_num_rows($rs) == 0) {
        $mins = intval($ts->format("i")) % 5;
        if ($mins > 0){
            $ts = $ts->sub(new DateInterval("PT{$mins}M"));
        }
        $sql = sprintf(
            "SELECT * from camera_log WHERE valid = '%s'",
            $ts->format("Y-m-d H:i")
        );
        $rs = pg_exec($conn, $sql);
    }

    /* Now we compute the RADAR timestamp, yippee */
    $mins = intval($ts->format("i")) % 5;
    $radts = clone $ts;
    $radts->sub(new DateInterval("PT{$mins}M"));
} else {
    $ts = new DateTime();
    $sql = "SELECT * from camera_current WHERE valid > (now() - '30 minutes'::interval)";
    $rs = pg_exec($conn, $sql);
    $radts = new DateTime();
    $mins = intval($radts->format("i")) % 5;
    $radts = $radts->sub(new DateInterval("PT{$mins}M"));
}

/* Who was online and where did they look?  Hehe */
$cdrct = array();
for ($i = 0; $row = pg_fetch_array($rs); $i++) {
    $cdrct[$row["cam"]] = $row["drct"];
}

/* Finally we get to map rendering */
$map = new mapObj("../../data/gis/base4326.map");

/* Hard coded extents based on network */
if ($network == "KCCI")
    $map->setExtent(-95.1, 40.55, -92.2, 43.4);
elseif ($network == "IDOT")
    $map->setExtent(-95.5, 39.7, -91.2, 44.6);
elseif ($network == "KELO")
    $map->setExtent(-98.8, 42.75, -95.9, 45.6);
elseif ($network == "KCRG")
    $map->setExtent(-93.0, 40.9, -90.1, 43.7);
$map->setSize(320, 240);

$namer = $map->getLayerByName("namerica");
$namer->__set("status", 1);

$stlayer = $map->getLayerByName("states");
$stlayer->__set("status", 1);

$counties = $map->getLayerByName("uscounties");
$counties->__set("status", 1);

$c0 = $map->getLayerByName("sbw");
$c0->__set("status", MS_ON);
$db_ts = $ts->format("Y-m-d H:i");
$year = $ts->format("Y");
$c0->__set("data", "geom from "
    . " (select significance, phenomena, geom, random() as oid from sbw "
    . " WHERE vtec_year = $year and polygon_end > '$db_ts' and "
    ." polygon_begin <= '$db_ts' and issue <= '$db_ts' "
    . " and significance = 'W' ORDER by phenomena ASC) as foo "
    . " using unique oid using SRID=4326");

$radar = $map->getLayerByName("nexrad_n0q");
$radar->__set("status", MS_ON);
$radts->setTimezone(new DateTimeZone("UTC"));
$fp = "/mesonet/ARCHIVE/data/" . $radts->format('Y/m/d/') . "GIS/uscomp/n0r_" . $radts->format('YmdHi') . ".png";
if (file_exists($fp)) {
    $radar->__set("data", $fp);
    $title = "RADAR";
    $y = 10;
} else {
    $radar->__set("status", MS_OFF);
    $title = "RADAR Unavailable\n";
    $y = 20;
}

$cp = new layerObj($map);
$cp->setProjection("epsg:4326");
$cp->__set("type", MS_SHAPE_POINT);
$cp->__set("status", MS_ON);
$cp->__set("labelcache", MS_ON);
$cl = new classObj($cp);
$lbl = new labelObj();
$cl->addLabel($lbl);
$cl->getLabel(0)->__set("size", 10);
$cl->getLabel(0)->__set("position", MS_CR);
$cl->getLabel(0)->__set("font", "liberation-bold");
$cl->getLabel(0)->__set("force", MS_ON);
$cl->getLabel(0)->__set("offsetx", 6);
$cl->getLabel(0)->__set("offsety", 0);
$cl->getLabel(0)->outlinecolor->setRGB(255, 255, 255);
$cl->getLabel(0)->color->setRGB(0, 0, 0);

$cl2 = new classObj($cp);
$lbl = new labelObj();
$cl2->addLabel($lbl);
$cl2->getLabel(0)->__set("size", "10");
$cl2->getLabel(0)->__set("font", "esri34");
$cl2->getLabel(0)->__set("position", MS_CC);
$cl2->getLabel(0)->__set("force", MS_ON);
$cl2->getLabel(0)->__set("partials", MS_ON);
$cl2->getLabel(0)->outlinecolor->setRGB(0, 0, 0);
$cl2->getLabel(0)->color->setRGB(255, 255, 255);

$img = $map->prepareImage();
$namer->draw($map, $img);
$counties->draw($map, $img);
$stlayer->draw($map, $img);
$radar->draw($map, $img);
$c0->draw($map, $img);

/* Draw Points */
foreach ($cdrct as $key => $drct) {
    if ($cameras[$key]["network"] != $network) continue;
    $lon = $cameras[$key]['lon'];
    $lat = $cameras[$key]['lat'];

    $pt = new pointObj();
    $pt->setXY($lon, $lat, 0);
    $pt->draw($map, $cp, $img, 0, intval(substr($key, 5, 3)));

    if ($cdrct[$key] >= 0 && $network != 'IDOT') {
        $pt = new pointObj();
        $pt->setXY($lon, $lat, 0);
        $cl2->getLabel(0)->__set("angle", (0 - $cdrct[$key]) + 90);
        $pt->draw($map, $cp, $img, 1, 'a');
    }
}
$d = $ts->format("m/d/Y h:i A");

$layer = $map->getLayerByName("credits");
$point = new pointobj();
$point->setXY(5, $y);
$point->draw($map, $layer, $img, 0,  "{$title}: $d");

$map->drawLabelCache($img);

header("Content-type: image/png");
echo $img->getBytes();
