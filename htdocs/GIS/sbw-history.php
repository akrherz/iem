<?php
require_once "/usr/lib64/php/modules/mapscript.php";

/* Generate an ultra fancy plot of a storm based warning history! */
require_once "../../config/settings.inc.php";
require_once "../../include/database.inc.php";
require_once "../../include/vtec.php";
require_once "../../include/forms.php";
require_once "../../include/mlib.php";

$mapFile = "../../data/gis/base4326.map";
$postgis = iemdb("postgis");

/* Figure out what our VTEC is! */
$vtec = isset($_GET["vtec"]) ? xssafe($_GET["vtec"]) : '2008.KICT.SV.W.0345';

list($year, $wfo, $phenomena, $significance, $eventid) = explode(".", $vtec);
$utcnow = new DateTime('now', new DateTimeZone("UTC"));
$eventid = intval(xssafe($eventid));
$year = intval(xssafe($year));
if (($year > (intval($utcnow->format("Y")) + 1)) || ($year < 1980)) {
    xssafe("<script>");
}
$wfo = substr(xssafe($wfo), 1, 3);
$phenomena = substr(xssafe($phenomena), 0, 2);
$significance = substr(xssafe($significance), 0, 1);

$rs = pg_prepare(
    $postgis,
    "SELECT",
    "SELECT polygon_begin at time zone 'UTC' as utc_polygon_begin, ".
    "ST_xmax(geom), ST_ymax(geom),
        ST_xmin(geom), ST_ymin(geom), *,
        round((ST_area2d(ST_transform(geom,9311))/1000000)::numeric,0 ) as area
        from sbw_$year WHERE phenomena = $1 and 
        eventid = $2 and wfo = $3 and significance = $4
        ORDER by polygon_begin ASC");

$rs = pg_execute($postgis, "SELECT", array($phenomena, $eventid, $wfo, $significance));

$rows = pg_num_rows($rs);

if ($rows < 2) {
    $width = 640;
    $height = 540;
    $twidth = 636;
    $theight = 476;
    $px = array(3,);
    $py = array(50,);
} else if ($rows >= 2 && $rows < 5) {
    $width = 640;
    $height = 540;
    $twidth = 316;
    $theight = 236;
    $px = array(3, 323, 3, 323);
    $py = array(50, 50, 290, 290);
} else {
    $width = 640;
    $height = 540;
    $twidth = 206;
    $theight = 154;
    $px = array(10, 220, 430, 10, 220, 430, 10, 220, 430);
    $py = array(60, 60, 60, 230, 230, 230, 390, 390, 390);
}

$map2 = new mapObj($mapFile);
$map2->imagecolor->setrgb(155, 155, 155);
$map2->setSize($width, $height);
$img2 = $map2->prepareImage();

$buffer = 0.3;

$xmax = 0;
$ymax = 0;
$xmin = 0;
$xmax = 0;
$gdimg_dest = null;
for ($i = 0; $row = pg_fetch_array($rs); $i++) {
    if ($i > 8) {
        continue;
    }
    if ($i == 0) {
        $xmax = $row["st_xmax"];
        $ymax = $row["st_ymax"];
        $xmin = $row["st_xmin"];
        $ymin = $row["st_ymin"];
        $xspace = $xmax - $xmin;
        $yspace = ($ymax - $ymin) * 1.5;
        $cross = ($xspace >= $yspace) ? $xspace : $yspace;
        $xc = $xmin + ($xmax - $xmin) / 2;
        $yc = $ymin + ($ymax - $ymin) / 2;
        $xmin = $xc - ($cross / 2) - $buffer;
        $ymin = $yc - ($cross / 2) - (.5 * $buffer);
        $ymax = $yc + ($cross / 2) + (1.5 * $buffer);
        $xmax = $xc + ($cross / 2) + $buffer;
        $bar640t = $map2->getLayerByName("bar640t");
        $bar640t->__set("status", MS_ON);
        $bar640t->draw($map2, $img2);

        $tlayer = $map2->getLayerByName("bar640t-title");
        $point = new pointObj();
        $point->setXY(80, 8);
        if ($rows > 8) {
            $point->draw($map2, $tlayer, $img2, 0, "Storm Based Warning History (First 9 shown)");
        } else {
            $point->draw($map2, $tlayer, $img2, 0, "Storm Based Warning History");
        }

        $point = new pointObj();
        $point->setXY(80, 25);
        $d = date("d M Y h:i A T",  strtotime($row["init_expire"]));
        $point->draw($map2, $tlayer, $img2, 1, "$wfo " . $vtec_phenomena[$phenomena] . " " . $vtec_significance[$significance] . " #$eventid till  $d");

        $layer = $map2->getLayerByName("logo");
        $point = new pointObj();
        $point->setXY(40, 26);
        $point->draw($map2, $layer, $img2, 0, "");

        $map2->drawLabelCache($img2);
        $gdimg_dest = imagecreatefromstring($img2->getBytes());

        $sz0 = ($row["area"] < 0.001) ? 0.001 : $row["area"];
    }

    $map = new mapObj($mapFile);
    $map->__set("width", $twidth);
    $map->__set("height", $theight);
    $map->setExtent($xmin, $ymin, $xmax, $ymax);

    $img = $map->prepareImage();

    $namerica = $map->getLayerByName("namerica");
    $namerica->__set("status", MS_ON);
    $namerica->draw($map, $img);

    $lakes = $map->getLayerByName("lakes");
    $lakes->__set("status", MS_ON);
    $lakes->draw($map, $img);

    $polygon_begin = new DateTime($row["utc_polygon_begin"], new DateTimeZone("UTC"));
    // Ensure we have a timestamp modulo 5 minutes to match archive RADAR
    $radts = clone $polygon_begin;
    $mins = intval($radts->format("i")) % 5;
    if ($mins > 0) {
        $radts->sub(new DateInterval("PT{$mins}M"));
    }
    $rtype = (intval($radts->format("Y")) > 2010) ? "n0q": "n0r";
    $radarfn = sprintf(
        "/mesonet/ARCHIVE/data/%s/GIS/uscomp/{$rtype}_%s.png",
        $radts->format("Y/m/d"),
        $radts->format("YmdHi"),
    );
    if (is_file($radarfn)) {
        $radar = $map->getLayerByName("nexrad_{$rtype}");
        $radar->__set("status", MS_ON);
        $radar->__set("data", $radarfn);
        $radar->draw($map, $img);
    }

    $counties = $map->getLayerByName("uscounties");
    $counties->__set("status", MS_ON);
    $counties->draw($map, $img);

    $states = $map->getLayerByName("states");
    $states->__set("status", MS_ON);
    $states->draw($map, $img);

    $wc = new layerObj($map);
    $wc->setConnectionType(MS_POSTGIS, "");
    $wc->__set("connection", get_dbconn_str("postgis"));
    $wc->__set("status", MS_ON);
    $sql = sprintf(
        "geom from (select random() as oid, geom from sbw_$year " .
            "WHERE phenomena = '%s' and wfo = '%s' and eventid = %s and " .
            "significance = '%s' and status = 'NEW') as foo using unique oid " .
            "using SRID=4326",
        $phenomena,
        $wfo,
        $eventid,
        $significance
    );
    $wc->__set("data", $sql);
    $wc->__set("type", MS_LAYER_LINE);
    $wc->setProjection("init=epsg:4326");

    $wcc0 = new classObj($wc);
    $wcc0s0 = new styleObj($wcc0);
    $wcc0s0->color->setRGB(255, 255, 255);
    $wcc0s0->__set("width", 2);
    $wcc0s0->__set("symbol", 'circle');
    $wc->draw($map, $img);
    $map->drawLabelCache($img);

    $wc = new layerObj($map);
    $wc->setConnectionType(MS_POSTGIS, "");
    $wc->__set("connection", get_dbconn_str("postgis"));
    $wc->__set("status", MS_ON);
    $sql = sprintf(
        "geom from (select random() as oid, geom from sbw_$year " .
            "WHERE phenomena = '%s' and wfo = '%s' and eventid = %s and " .
            "significance = '%s' and polygon_begin = '%s') as foo " .
            "using unique oid using SRID=4326",
        $phenomena,
        $wfo,
        $eventid,
        $significance,
        $row["polygon_begin"]
    );
    $wc->__set("data", $sql);
    $wc->__set("type", MS_LAYER_LINE);
    $wc->setProjection("init=epsg:4326");

    $wcc0 = new classObj($wc);
    $wcc0->__set("name", $row["area"] . " sq km [" . intval($row["area"] / $sz0 * 100) . "%]");
    $wcc0s0 = new styleObj($wcc0);
    $wcc0s0->color->setRGB(255, 0, 0);
    $wcc0s0->__set("width", 3);
    $wcc0s0->__set("symbol", 'circle');
    $wc->draw($map, $img);
    $map->drawLabelCache($img);

    $bar640t = $map->getLayerByName("bar640t");
    $bar640t->__set("status", 1);
    $bar640t->draw($map, $img);

    $tlayer = $map->getLayerByName("bar640t-title");
    $point = new pointObj();
    $point->setXY(2, 8);
    $point->draw($map, $tlayer, $img, 0, $vtec_status[$row["status"]]);

    $point = new pointObj();
    $point->setXY(2, 25);
    $d = date("d M Y h:i A T",  strtotime($row["polygon_begin"]));
    $point->draw($map, $tlayer, $img, 1, "$d");

    $map->embedLegend($img);
    $map->drawLabelCache($img);
    $gdimg_src = imagecreatefromstring($img->getBytes());
    imagecopy(
        $gdimg_dest,
        $gdimg_src,
        $px[$i],
        $py[$i],
        0,
        0,
        $twidth,
        $theight,
    );
    imagedestroy($gdimg_src);
}
header("Content-type: image/png");
if (is_null($gdimg_dest)){
    $gdimg_dest = imagecreatefromstring($img2->getBytes());
}
echo imagepng($gdimg_dest);
