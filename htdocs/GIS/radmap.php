<?php
/* 
 * I am sort of inspired by the old mapblaster days.  Lets create a map of
 * all sorts of data with tons of CGI vars, yippeee
 * 
 */
require_once "/usr/lib64/php/modules/mapscript.php";

require_once "../../config/settings.inc.php";
require_once "../../include/database.inc.php";
require_once "../../include/vtec.php";
require_once "../../include/forms.php";
$postgis = iemdb("postgis");

$plotmeta = array(
    "title" => array(),
    "subtitle" => ""
);

function draw_header($map, $img, $width, $height)
{
    /*
     * Draw the black bar at the top of the screen
     */
    $layer = new LayerObj($map);
    $layer->status = MS_ON;
    $layer->type = MS_LAYER_POLYGON;
    $layer->transform = MS_OFF;
    $wkt = "POLYGON((0 0, 0 $height, $width $height, $width 0, 0 0))";
    $shp = shapeObj::fromWKT($wkt);
    $layer->addFeature($shp);

    $layerc0 = new ClassObj($layer);
    $layerc0s0 = new StyleObj($layerc0);
    $layerc0s0->color->setRGB(0, 0, 0);
    $layer->draw($map, $img);
}

function get_goes_fn_and_time($ts, $sector, $product)
{
    /*
     * Return a filename or NULL for a requested GOES Product and time
     * using a crude search algorithm
     */
    $base = "/mesonet/ARCHIVE/data/";
    for ($i = 0; $i < 60; $i++) {
        foreach (array(1, -1) as $mul) {
            $lts = clone $ts;
            $mins = $i * $mul;
            if ($mins > 0) $lts->add(new DateInterval("PT{$mins}M"));
            $testfn = $base . $lts->format("Y/m/d") . "/GIS/sat/awips211/GOES_{$sector}_{$product}_" .
                $lts->format("YmdHi") . ".png";
            if (is_file($testfn)) {
                return array($testfn, $lts);
            }
        }
    }
    return array(NULL, NULL);
}

function get_ridge_fn_and_time($ts, $radar, $product)
{
    /*
     * Return a filename or NULL for a requested RIDGE Product and time
     * using a crude search algorithm
     */
    $base = "/mesonet/ARCHIVE/data/";
    for ($i = 0; $i < 10; $i++) {
        foreach (array(1, -1) as $mul) {
            $lts = clone $ts;
            if ($i < 0) $lts->sub(new DateInterval("PT{$i}M"));
            else $lts->add(new DateInterval("PT{$i}M"));
            $testfn = $base . $lts->format("Y/m/d") . "/GIS/ridge/$radar/$product/{$radar}_{$product}_" .
                $lts->format("YmdHi") . ".png";
            if (is_file($testfn)) {
                return array($testfn, $lts);
            }
        }
    }
    return array(NULL, NULL);
}

$sectors = array(
    "iem" => array("epsg" => 4326, "ext" => array(-100.0, 38.5, -88.0, 46.5)),
    "lot" => array("epsg" => 4326, "ext" => array(-94.8, 39.0, -83.5, 46.5)),
    "ict" => array("epsg" => 4326, "ext" => array(-102.4, 35.45, -94.4, 40.35)),
    "sd" => array("epsg" => 4326, "ext" => array(-105.5, 40.5, -95.5, 48.0)),
    "hun" => array("epsg" => 4326, "ext" => array(-90.0, 32.0, -84.0, 36.0)),
    "conus" => array(
        "epsg" => 2163,
        "ext" => array(-2110437, -2251067, 2548326, 1239063)
    ),
    "texas" => array(
        "epsg" => 2163,
        "ext" => array(-532031.375, -2133488, 723680.125, -959689.625)
    ),
    "etexas" => array(
        "epsg" => 2163,
        "ext" => array(-132031.375, -1933488, 623680.125, -1259689.625)
    ),
    "florida" => array(
        "epsg" => 2163,
        "ext" => array(1184257, -2271667, 2198502, -1189456)
    ),
    "maine" => array(
        "epsg" => 2163,
        "ext" => array(2201008.54544837, 209411.348773363, 2516387.56069489, 732383.197334035)
    ),
    "michigan" => array(
        "epsg" => 26915,
        "ext" => array(697867.530690471, 4641622.22153389, 1363156.86711036, 5347664.58607328)
    ),
    "washington" => array(
        "epsg" => 2163,
        "ext" => array(-1816611.94664531, 247411.313142634, -1231350.67314885, 688254.98213837)
    ),
    "california" => array(
        "epsg" => 2163,
        "ext" => array(-2031905.01470961, -1244659.20932869, -1296945.03256045, -39583.1960413812)
    ),
);

/* Setup layers */
$layers = isset($_GET["layers"]) ? $_GET["layers"] : array("n0q");
// Make sure layers is an array...
if (gettype($layers) == "string") {
    $layers = array($layers);
}

/* Straight CGI Butter */
$sector = isset($_GET["sector"]) ? $_GET["sector"] : "iem";
$width = get_int404("width", 640);
$height = get_int404("height", 480);
$lsrbuffer = get_int404("lsrbuffer", 15);

// Now, maybe we set a VTEC string, lets do all sorts of fun
$vtec_limiter = "";
if (isset($_GET["vtec"])) {
    $cvtec = xssafe($_GET["vtec"]);
    // cull errand _
    $pos = strpos($cvtec, "_");
    if ($pos !== false) {
        $cvtec = substr($cvtec, 0, $pos);
    }
    // we may have gotten here with '-' or '.' in vtec string, rectify
    $cvtec = str_replace("-", ".", strtoupper($cvtec));
    $tokens = explode(".", $cvtec);
    if (sizeof($tokens) == 7) {
        list(
            $year, $pclass, $status, $wfo, $phenomena, $significance,
            $eventid
        ) = explode(".", $cvtec);
    } else {
        list(
            $year, $wfo, $phenomena, $significance,
            $eventid
        ) = explode(".", $cvtec);
    }
    $eventid = intval($eventid);
    $year = intval($year);
    if ($year < 1980 || $year > 2030){
        xssafe("<script>");
    }
    $wfo = substr($wfo, 1, 3);
    // Try to find this warning as a polygon first, then look at warnings table
    $sql = <<<EOF
      with one as (
          SELECT max(issue at time zone 'UTC') as v,
          max(expire at time zone 'UTC') as e, ST_extent(geom),
          max('P')::text as gtype
          from sbw_{$year}
          WHERE wfo = $1 and phenomena = $2 and eventid = $3 and
          significance = $4 and status = 'NEW'),
      two as (
          SELECT max(issue at time zone 'UTC') as v,
          max(expire at time zone 'UTC') as e, ST_extent(u.geom),
          'C'::text as gtype from warnings_{$year} w JOIN ugcs u on (w.gid = u.gid)
          WHERE w.wfo = $1 and phenomena = $2 and eventid = $3 and
          significance = $4),
      agg as (SELECT * from one UNION ALL select * from two)

      SELECT v, e, ST_xmax(st_extent) as x1, st_xmin(st_extent) as x0,
      ST_ymax(st_extent) as y1, st_ymin(st_extent) as y0, gtype from agg
      WHERE gtype is not null and v is not null LIMIT 1
EOF;
    $rs = pg_prepare($postgis, "OOR", $sql);
    $rs = pg_execute($postgis, "OOR", array(
        $wfo, $phenomena, $eventid,
        $significance
    ));
    if ($rs === FALSE || pg_num_rows($rs) != 1) exit("ERROR: Unable to find warning!");
    $row = pg_fetch_assoc($rs, 0);
    $lpad = 0.5;
    $y1 = $row["y1"] + $lpad;
    $y0 = $row["y0"] - $lpad;
    $x1 = $row["x1"] + $lpad;
    $x0 = $row["x0"] - $lpad;
    $xc = $x0 + ($row["x1"] - $row["x0"]) / 2;
    $yc = $y0 + ($row["y1"] - $row["y0"]) / 2;

    $sector = "custom";
    $sectors["custom"] = array("epsg" => 4326, "ext" => array($x0, $y0, $x1, $y1));

    // Now the concern here is what to do with the valid time of this plot
    // If now() is less than event end, set the plot time to now
    $dts = new DateTime($row["v"], new DateTimeZone("UTC"));
    $dts2 = new DateTime($row["e"], new DateTimeZone("UTC"));
    $aa = new DateTime('now', new DateTimeZone('UTC'));
    if ($dts2 > $aa) {
        $dts = new DateTime('now', new DateTimeZone('UTC'));
    }

    $vtec_limiter = sprintf(
        "and phenomena = '%s' and eventid = %s and 
        significance = '%s' and w.wfo = '%s'",
        $phenomena,
        $eventid,
        $significance,
        $wfo
    );
    if ($row["gtype"] == 'P') {
        $layers[] = 'sbw';
    } else {
        $layers[] = 'cbw';
    }
}
if (isset($_REQUEST['pid'])) {
    $pid = $_REQUEST["pid"];
    $dts = DateTime::createFromFormat(
        "YmdHi",
        substr($_GET["pid"], 0, 12),
        new DateTimeZone("UTC"),
    );
    /* First, we query for a bounding box please */
    $rs = pg_prepare(
        $postgis,
        "SELECTPID",
        "SELECT ST_xmax(ST_extent(geom)) as x1, ST_xmin(ST_extent(geom)) as x0, "
            . "ST_ymin(ST_extent(geom)) as y0, ST_ymax(ST_extent(geom)) as y1 "
            . "from sps WHERE product_id = $1"
    );
    $result = pg_execute($postgis, "SELECTPID", array($pid));
    $row = pg_fetch_array($result, 0);
    $lpad = 0.5;
    $y1 = $row["y1"] + $lpad;
    $y0 = $row["y0"] - $lpad;
    $x1 = $row["x1"] + $lpad;
    $x0 = $row["x0"] - $lpad;
    $xc = $x0 + ($row["x1"] - $row["x0"]) / 2;
    $yc = $y0 + ($row["y1"] - $row["y0"]) / 2;
    $sector = "custom";
    $sectors["custom"] = array("epsg" => 4326, "ext" => array($x0, $y0, $x1, $y1));
}

/* Could define a custom box */
if (isset($_GET["bbox"])) {
    $sector = "custom";
    $bbox = isset($_GET["bbox"]) ? explode(",", $_GET["bbox"]) : die("No BBOX");
    $sectors["custom"] = array("epsg" => 4326, "ext" => $bbox);
}
/* Fetch bounds based on wfo as being set by bounds */
if ($sector == "wfo") {
    $sector_wfo = isset($_REQUEST["sector_wfo"]) ? strtoupper($_REQUEST["sector_wfo"]) : "DMX";
    /* Fetch the bounds */
    pg_prepare($postgis, "WFOBOUNDS", "SELECT ST_xmax(geom) as xmax, ST_ymax(geom) as ymax, "
        . " ST_xmin(geom) as xmin, ST_ymin(geom) as ymin from "
        . " (SELECT ST_Extent(geom) as geom from ugcs WHERE "
        . " wfo = $1 and end_ts is null) as foo");
    $rs = pg_execute($postgis, "WFOBOUNDS", array($sector_wfo));
    if (pg_num_rows($rs) > 0) {
        $row = pg_fetch_assoc($rs, 0);
        $buffer = 0.25;
        $sectors["wfo"] = array(
            "epsg" => 4326,
            "ext" => array(
                $row["xmin"] - $buffer, $row["ymin"] - $buffer,
                $row["xmax"] + $buffer, $row["ymax"] + $buffer
            )
        );
    }
}

/* Lets determine our timestamp.  Our options include
   1.  Specified by URI, $ts
   2.  They specified a VTEC string, use that
   3.  Nothing specified, realtime!
*/

$utcnow = new DateTime('now', new DateTimeZone("UTC"));
$ts = isset($_GET["ts"]) ? DateTime::createFromFormat("YmdHi", $_GET["ts"], new DateTimeZone("UTC")) : $utcnow;
$ts1 = isset($_GET["ts1"]) ? DateTime::createFromFormat("YmdHi", $_GET["ts1"], new DateTimeZone("UTC")) : null;
$ts2 = isset($_GET["ts2"]) ? DateTime::createFromFormat("YmdHi", $_GET["ts2"], new DateTimeZone("UTC")) : null;
if (isset($dts) && !isset($_GET["ts"])) {
    $ts = clone $dts;
}
if (is_null($ts1)) {
    $ts1 = clone $ts;
}
if (isset($dts2) && !isset($_GET["ts2"])) {
    $ts2 = clone $dts2;
}
/* Make sure we have a minute %5 */
$radts = clone $ts;
$mins = intval($ts->format("i")) % 5;
if ($mins > 0) {
    $radts->sub(new DateInterval("PT{$mins}M"));
}

/* Lets Plot stuff already! */
$mapFile = "../../data/gis/base" . $sectors[$sector]['epsg'] . ".map";
$map = new mapObj($mapFile);
$map->setSize($width, $height);
$map->setExtent(
    $sectors[$sector]['ext'][0],
    $sectors[$sector]['ext'][1],
    $sectors[$sector]['ext'][2],
    $sectors[$sector]['ext'][3]
);
if (in_array("n0q", $layers) || in_array("ridge", $layers) || in_array("prn0q", $layers) || in_array("akn0q", $layers) || in_array("hin0q", $layers)) {
    $map->selectOutputFormat("png24");
}

$img = $map->prepareImage();

$namerica = $map->getLayerByName("namerica");
$namerica->status = MS_ON;
$namerica->draw($map, $img);

$lakes = $map->getLayerByName("lakes");
$lakes->status = MS_ON;
$lakes->draw($map, $img);

$places = $map->getLayerByName("places2010");
$places->status = in_array("places", $layers);
$places->draw($map, $img);

if (
    in_array("goes", $layers) && isset($_REQUEST["goes_sector"]) &&
    isset($_REQUEST["goes_product"])
) {
    $res = get_goes_fn_and_time(
        $ts,
        strtoupper($_REQUEST["goes_sector"]),
        strtoupper($_REQUEST["goes_product"])
    );
    if ($res[0] != NULL) {
        $radar = $map->getLayerByName("east_vis_1km");
        $radar->status = MS_ON;
        $radar->data = $res[0];
        $radar->draw($map, $img);

        $plotmeta["subtitle"] .= sprintf(
            " GOES %s %s %s ",
            $_REQUEST["goes_sector"],
            $_REQUEST["goes_product"],
            $res[1]->format("h:i A e")
        );
    }
}



if (in_array("nexrad", $layers) || in_array("nexrad_tc", $layers)  || in_array("nexrad_tc6", $layers)) {
    $radarfp = "/mesonet/ldmdata/gis/images/4326/USCOMP/n0r_0.tif";
    $tss = clone $ts;
    $tss->add(new DateInterval("PT5M"));
    if ($tss < $utcnow) {
        $radarfp = sprintf(
            "/mesonet/ARCHIVE/data/%s/GIS/uscomp/n0r_%s.png",
            $radts->format("Y/m/d"),
            $radts->format("YmdHi"),
        );
    }
    if (in_array("nexrad_tc", $layers)) {
        $radarfp = sprintf(
            "/mesonet/ARCHIVE/data/%s/GIS/uscomp/max_n0r_0z0z_%s.png",
            $ts->format("Y/m/d"),
            $ts->format("Ymd"),
        );
    }
    if (in_array("nexrad_tc6", $layers)) {
        $radarfp = sprintf(
            "/mesonet/ARCHIVE/data/%s/GIS/uscomp/max_n0r_6z6z_%s.png",
            $ts->format("Y/m/d"),
            $ts->format("Ymd"),
        );
    }
    if (is_file($radarfp)) {
        $radar = $map->getLayerByName("nexrad_n0r");
        $radar->status = MS_ON;
        $radar->data = $radarfp;
        $radar->draw($map, $img);
    }
}

/* Draw NEXRAD Layer */
$prefixes = array("" => "us", "ak" => "ak", "pr" => "pr", "hi" => "hi");
foreach ($prefixes as $p1 => $p2) {
    if (in_array("{$p1}n0q", $layers) || in_array("{$p1}n0q_tc", $layers) || in_array("{$p1}n0q_tc6", $layers)) {
        $radarfp = sprintf("/mesonet/ldmdata/gis/images/4326/%sCOMP/n0q_0.png", strtoupper($p2));
        $tss = clone $ts;
        $tss->add(new DateInterval("PT5M"));
        if ($tss < $utcnow) {
            $radarfp = sprintf(
                "/mesonet/ARCHIVE/data/%s/GIS/%scomp/n0q_%s.png",
                $radts->format("Y/m/d"),
                $p2,
                $radts->format("Ymd"),
            );
        }
        if (in_array("{$p1}n0q_tc", $layers)) {
            $radarfp = sprintf(
                "/mesonet/ARCHIVE/data/%s/GIS/%scomp/max_n0q_0z0z_%s.png",
                $ts->format("Y/m/d"),
                $p2,
                $ts->format("Ymd"),
            );
        }
        if (in_array("{$p1}n0q_tc6", $layers)) {
            $radarfp = sprintf(
                "/mesonet/ARCHIVE/data/%s/GIS/%scomp/max_n0q_6z6z_%s.png",
                $ts->format("Y/m/d"),
                $p2,
                $ts->format("YmdHi"),
            );
        }
        if (is_file($radarfp)) {
            $radar = $map->getLayerByName("nexrad_n0q");
            $radar->status = MS_ON;
            $radar->data = $radarfp;
            $radar->draw($map, $img);
        }
        break;
    }
}


if (
    in_array("ridge", $layers) && isset($_REQUEST["ridge_radar"]) &&
    isset($_REQUEST["ridge_product"])
) {
    $res = get_ridge_fn_and_time(
        $ts,
        strtoupper($_REQUEST["ridge_radar"]),
        strtoupper($_REQUEST["ridge_product"])
    );
    if ($res[0] != NULL) {
        $radar = $map->getLayerByName("nexrad_n0q");
        $radar->status = MS_ON;
        $radar->data = $res[0];
        $radar->draw($map, $img);
        $plotmeta["subtitle"] .= sprintf(
            " RIDGE %s %s %s ",
            $_REQUEST["ridge_radar"],
            $_REQUEST["ridge_product"],
            $res[1]->format("h:i A e")
        );
    }
}

$states = $map->getLayerByName("states");
$states->status = MS_ON;
$states->draw($map, $img);

/* All SBWs for a WFO */
if (in_array("allsbw", $layers) && isset($_REQUEST["sector_wfo"])) {
    $sbwh = $map->getLayerByName("allsbw");
    $sbwh->status =  MS_ON;
    $sbwh->connection = get_dbconn_str("postgis");
    $sql = sprintf(
        "geom from (select phenomena, geom, random() as oid from sbw "
            . "WHERE significance = 'W' and status = 'NEW' and wfo = '%s' and "
            . "phenomena in ('SV') "
            . "and issue > '2007-10-01') as foo "
            . "using unique oid using SRID=4326",
        $sector_wfo
    );
    $sbwh->data = $sql;
    $sbwh->draw($map, $img);
}
$counties = $map->getLayerByName("uscounties");
$counties->status = in_array("uscounties", $layers);
$counties->draw($map, $img);

$cwas = $map->getLayerByName("cwas");
$cwas->status = in_array("cwas", $layers);
$cwas->draw($map, $img);

/* Buffered LSRs */
if (in_array("bufferedlsr", $layers)) {
    $blsr = new LayerObj($map);
    $blsr->setConnectionType(MS_POSTGIS, "");
    $blsr->connection = get_dbconn_str("postgis");
    $blsr->status = in_array("bufferedlsr", $layers);
    $sql = "geo from (select distinct city, magnitude, valid, "
        . "ST_Transform(ST_Buffer(ST_Transform(geom,2163),{$lsrbuffer}000),4326) as geo, "
        . "type as ltype, city || magnitude || ST_x(geom) || ST_y(geom) as k "
        . "from lsrs WHERE "
        . "ST_Overlaps((select geom from sbw_" . $ts->format("Y") . " WHERE "
        . "wfo = '$wfo' and phenomena = '$phenomena' and "
        . "significance = '$significance' and eventid = $eventid "
        . "and status = 'NEW' LIMIT 1), "
        . "ST_Transform(ST_Buffer(ST_Transform(geom,2163),{$lsrbuffer}000),4326) "
        . ") and "
        . "valid >= '" . $ts->format("Y-m-d H:i") . "' and "
        . "valid < '" . $ts2->format("Y-m-d H:i") . "' and "
        . "((type = 'M' and magnitude >= 34) or "
        . "(type = 'H' and magnitude >= 0.75) or type = 'W' or "
        . "type = 'T' or (type = 'G' and magnitude >= 58) or type = 'D' "
        . "or type = 'F') ORDER by valid DESC) as foo "
        . "USING unique k USING SRID=4326";
    $blsr->data = $sql;
    $blsr->type = MS_LAYER_POLYGON;
    $blsr->setProjection("init=epsg:4326");
    $blc0 = new ClassObj($blsr);
    $blc0->name = "Buffered LSRs ({$lsrbuffer} km)";
    $blc0s0 = new StyleObj($blc0);
    $blc0s0->symbolname = 'circle';
    $blc0s0->color->setRGB(0, 0, 0);
    $blc0s0->outlinecolor->setRGB(50, 50, 50);
    $blsr->draw($map, $img);
}

/* Watch by County */
$wbc = $map->getLayerByName("watch_by_county");
$wbc->status = in_array("watch_by_county", $layers);
$wbc->connection = get_dbconn_str("postgis");
$sql = sprintf(
    "g from (select phenomena, eventid, " .
        "ST_buffer(ST_collect(u.simple_geom), 0) as g " .
        "from warnings w JOIN ugcs u " .
        "on (u.gid = w.gid) WHERE " .
        "significance = 'A' and phenomena IN ('TO','SV') and " .
        "issue <= '%s:00+00' and expire > '%s:00+00' " .
        "GROUP by phenomena, eventid ORDER by phenomena ASC) as foo " .
        "using SRID=4326 using unique phenomena",
    $ts->format("Y-m-d H:i"),
    $ts->format("Y-m-d H:i")
);
$wbc->data = $sql;
$wbc->draw($map, $img);

$watches = $map->getLayerByName("watches");
$watches->status = in_array("watches", $layers);
$watches->connection = get_dbconn_str("postgis");
$sql = sprintf(
    "geom from (select type as wtype, geom, num from watches "
        . "WHERE issued <= '%s:00+00' and expired > '%s:00+00') as foo "
        . "using SRID=4326 using unique num",
    $ts->format("Y-m-d H:i"),
    $ts->format("Y-m-d H:i")
);
$watches->data = $sql;
$watches->draw($map, $img);

/* Plot the warning explicitly */
if (isset($_REQEST["pid"])) {
    $wc = new LayerObj($map);
    $wc->setConnectionType(MS_POSTGIS, "");
    $wc->connection = get_dbconn_str("postgis");
    $wc->status = MS_ON;
    $sql = sprintf("geom from (select geom, product_id from sps "
        . "WHERE product_id = '$pid') as foo using unique product_id using SRID=4326");
    $wc->data = $sql;
    $wc->type = MS_LAYER_LINE;
    $wc->setProjection("init=epsg:4326");

    $wcc0 = new ClassObj($wc);
    $wcc0->name = "Product";
    $wcc0s0 = new StyleObj($wcc0);
    $wcc0s0->color->setRGB(255, 0, 0);
    $wcc0s0->size = 3;
    $wcc0s0->symbolname = 'circle';
    $wc->draw($map, $img);
}


// Draws the county-based VTEC warning, only if "cbw" in $layers
if (isset($_REQUEST["vtec"]) && in_array("cbw", $layers)) {
    $wc = new LayerObj($map);
    $wc->setConnectionType(MS_POSTGIS, "");
    $wc->connection = get_dbconn_str("postgis");
    $wc->status = MS_ON;
    $sql = sprintf("geom from (select eventid, w.wfo, significance, "
        . "phenomena, u.geom, random() as oid from warnings_$year w JOIN ugcs u "
        . "on (u.gid = w.gid) WHERE w.wfo = '$wfo' "
        . "and phenomena = '$phenomena' and significance = '$significance' "
        . "and eventid = $eventid ORDER by phenomena ASC) as foo "
        . "using unique oid using SRID=4326");
    $wc->data = $sql;
    $wc->type = MS_LAYER_LINE;
    $wc->setProjection("init=epsg:4326");

    $wcc0 = new ClassObj($wc);
    $wcc0->name = $vtec_phenomena[$phenomena] . " " . $vtec_significance[$significance];
    $wcc0s0 = new StyleObj($wcc0);
    $wcc0s0->color->setRGB(255, 0, 0);
    $wcc0s0->width = 3;
    $wcc0s0->symbol = 'circle';
    $wc->draw($map, $img);
}

/* Storm based warning history, plotted as a white outline, I think */
if (in_array("sbwh", $layers) && intval($ts->format("Y")) > 2001) {
    $ptext = "'ZZ' as phenomena";
    $sbwh = $map->getLayerByName("sbw");
    $sbwh->status = MS_ON;
    $sbwh->connection = get_dbconn_str("postgis");
    $sql = sprintf(
        "geom from (select %s, geom, random() as oid from sbw_%s w "
            . "WHERE significance != 'A' and polygon_begin <= '%s:00+00' and "
            . "polygon_end > '%s:00+00' "
            . "%s) as foo using unique oid using SRID=4326",
        $ptext,
        $ts->format("Y"),
        $ts->format("Y-m-d H:i"),
        $ts->format("Y-m-d H:i"),
        $vtec_limiter
    );
    $sbwh->data = $sql;
    $sbwh->draw($map, $img);
}

/* Storm Based Warning */
if (in_array("sbw", $layers)  && intval($ts->format("Y")) > 2001) {
    $ptext = "phenomena";
    if (in_array("sbw", $layers) && in_array("cbw", $layers)) {
        $ptext = "'ZZ' as phenomena";
    }
    $sbw = $map->getLayerByName("sbw");
    $sbw->status = MS_ON;
    $sbw->connection = get_dbconn_str("postgis");
    $sql = sprintf(
        "geom from (select %s, geom, random() as oid from sbw_%s w "
            . "WHERE significance != 'A' and polygon_begin <= '%s:00+00' "
            . "and polygon_end > '%s:00+00' "
            . "%s) as foo using unique oid using SRID=4326",
        $ptext,
        $ts->format("Y"),
        $ts->format("Y-m-d H:i"),
        $ts->format("Y-m-d H:i"),
        $vtec_limiter
    );
    $sbw->data = $sql;
    $sbw->draw($map, $img);
}

/* warnings by county */
$w0c = $map->getLayerByName("warnings0_c");
$w0c->connection = get_dbconn_str("postgis");
$w0c->status = in_array("county_warnings", $layers);
$sql = sprintf(
    "geom from (select u.geom, phenomena, significance, "
        . "random() as oid from warnings_%s w JOIN ugcs u on (u.gid = w.gid) "
        . "WHERE issue <= '%s:00+00' and expire > '%s:00+00' %s "
        . "ORDER by phenomena ASC) as foo using unique oid using SRID=4326",
    $ts->format("Y"),
    $ts->format("Y-m-d H:i"),
    $ts->format("Y-m-d H:i"),
    $vtec_limiter
);
$w0c->data = $sql;
$w0c->draw($map, $img);

/* Local Storm Reports */
$lsrs = $map->getLayerByName("lsrs");
$lsrs->connection = get_dbconn_str("postgis");
$lsrs->status = in_array("lsrs", $layers);
if ($ts2 > $ts1) {
    $sql = "geom from (select distinct city, magnitude, valid, geom, "
        . "type as ltype, city || magnitude || ST_x(geom) || ST_y(geom) as k "
        . "from lsrs WHERE "
        . "valid >= '" . $ts1->format("Y-m-d H:i") . ":00+00' and "
        . "valid < '" . $ts2->format("Y-m-d H:i") . ":00+00' "
        . "ORDER by valid DESC) as foo USING unique k USING SRID=4326";
} else {
    $sql = "geom from (select distinct city, magnitude, valid, geom, "
        . "type as ltype, city || magnitude || ST_x(geom) || ST_y(geom) as k "
        . "from lsrs WHERE "
        . "valid = '" . $ts->format("Y-m-d H:i") . ":00+00') as foo "
        . "USING unique k USING SRID=4326";
}
$lsrs->data = $sql;
$lsrs->draw($map, $img);

/* County Intersection */
if (in_array("ci", $layers)) {
    $ci = new LayerObj($map);
    $ci->setConnectionType(MS_POSTGIS, "");
    $ci->connection = get_dbconn_str("postgis");
    $ci->status = in_array("ci", $layers);
    $tblyr = $ts->format("Y");
    $sql = <<<EOF
geo from (
    WITH stormbased as (SELECT geom from sbw_$tblyr where wfo = '$wfo' 
        and eventid = $eventid and significance = '$significance' 
        and phenomena = '$phenomena' and status = 'NEW'), 
    countybased as (SELECT ST_Union(u.geom) as geom from 
        warnings_$tblyr w JOIN ugcs u on (u.gid = w.gid) 
        WHERE w.wfo = '$wfo' and eventid = $eventid and 
        significance = '$significance' and phenomena = '$phenomena') 
                
    SELECT ST_SetSRID(ST_intersection(
          ST_buffer(ST_exteriorring(ST_geometryn(ST_multi(c.geom),1)),0.02),
          ST_exteriorring(ST_geometryn(ST_multi(s.geom),1))
       ), 4326) as geo,
    random() as k
    from stormbased s, countybased c
            
) as foo USING unique k USING SRID=4326
EOF;
    $ci->data = $sql;
    $ci->type = MS_LAYER_LINE;
    $ci->setProjection("init=epsg:4326");
    $cic0 = new ClassObj($ci);
    $cic0->name = "County Intersection";
    $cic0s0 = new StyleObj($cic0);
    $cic0s0->color->setRGB(250, 0, 250);
    $cic0s0->width = 5;
    $ci->draw($map, $img);
}

/* Interstates */
$interstates = $map->getLayerByName("interstates");
$interstates->status = in_array("interstates", $layers);
$interstates->draw($map, $img);

/* roads */
$roads = $map->getLayerByName("roads");
$roads->connection = get_dbconn_str("postgis");
$roads->status = in_array("roads", $layers);
$roads->draw($map, $img);

/* roads */
$roadsint = $map->getLayerByName("roads-inter");
$roadsint->connection = get_dbconn_str("postgis");
$roadsint->status = in_array("roads-inter", $layers);
$roadsint->draw($map, $img);

if (in_array("usdm", $layers)) {
    $usdm = $map->getLayerByName("usdm");
    $usdm->status = MS_ON;
    $usdm->draw($map, $img);
}

if (in_array("cities", $layers)) {
    $l = $map->getLayerByName("cities");
    $l->status = MS_ON;
    $l->draw($map, $img);
}

if (in_array("surface", $layers)) {
    $surface = $map->getLayerByName("surface");
    $surface->status = MS_ON;
    $surface->draw($map, $img);
}
if (in_array("airtemps", $layers)) {
    $airtemps = $map->getLayerByName("airtemps");
    $airtemps->status = MS_ON;
    if ($width > 800) {
        for ($i = 0; $i < $airtemps->numclasses; $i++) {
            $cl = $airtemps->getClass($i);
            $cllabel = $cl->getLabel(0);
            $cllabel->size = 20;
        }
    }
    $airtemps->draw($map, $img);
}

$tlayer = $map->getLayerByName("bar640t-title");
$point = new pointobj();
$point->setXY(80, 9);
$tzformat = "d M Y h:i A T";
$tzinfo = isset($_REQUEST["tz"]) ? xssafe($_REQUEST["tz"]) : "America/Chicago";
// Translate to ZoneInfo compat
if ($tzinfo == 'MDT' || $tzinfo == 'MST') {
    $tzinfo = "America/Denver";
} elseif ($tzinfo == 'PDT' || $tzinfo == 'PST') {
    $tzinfo = "America/Los_Angeles";
} elseif ($tzinfo == 'CDT' || $tzinfo == 'CST') {
    $tzinfo = "America/Chicago";
} elseif ($tzinfo == 'EDT' || $tzinfo == 'EST') {
    $tzinfo = "America/New_York";
}
if ($tzinfo == 'UTC') {
    $tzformat = "d M Y H:i T";
}
$lts = clone $ts;
$lts->settimezone(new DateTimeZone($tzinfo));
$d = $lts->format($tzformat);
$tomorrow = clone $ts;
$tomorrow->add(new DateInterval("P1D"));
if (isset($_GET["title"])) {
    $title = substr($_GET["title"], 0, 100);
} else if (isset($_GET["vtec"])) {
    $title = "VTEC ID: " . $_GET["vtec"];
} else if (in_array("nexrad", $layers)) {
    $title = "NEXRAD Base Reflectivity";
} else if (in_array("n0q", $layers) || in_array("akn0q", $layers) || in_array("hin0q", $layers) || in_array("prn0q", $layers)) {
    $title = "NEXRAD Base Reflectivity";
} else if (in_array("n0q_tc", $layers)) {
    $title = "IEM NEXRAD Daily N0Q Max Base Reflectivity";
    $d = sprintf(
        "Valid between %s 00:00 and 23:59 UTC",
        $ts->format("d M Y")
    );
} else if (in_array("n0q_tc6", $layers)) {
    $title = "IEM NEXRAD 24 Hour N0Q Max Base Reflectivity";
    $d = sprintf(
        "Valid between %s 06:00 and %s 05:55 UTC",
        $ts->format("d M Y"),
        $tomorrow->format("d M Y")
    );
} else if (in_array("nexrad_tc", $layers)) {
    $title = "IEM NEXRAD Daily N0R Max Base Reflectivity";
    $d = sprintf(
        "Valid between %s 00:00 and 23:59 UTC",
        $ts->format("d M Y")
    );
} else if (in_array("nexrad_tc6", $layers)) {
    $title = "IEM NEXRAD 24 Hour N0R Max Base Reflectivity";
    $d = sprintf(
        "Valid between %s 06:00 and %s 05:55 UTC",
        $ts->format("d M Y"),
        $tomorrow->format("d M Y")
    );
} else {
    $title = "IEM Plot";
    if ($plotmeta["subtitle"] != "") {
        $title = $plotmeta["subtitle"];
        $plotmeta["subtitle"] = "";
    }
}

$header_height = ($plotmeta["subtitle"] == "") ? 36 : 53;
draw_header($map, $img, $width, $header_height);

$point->draw($map, $tlayer, $img, 0, $title);

$point = new pointobj();
$point->setXY(80, 26);
$point->draw($map, $tlayer, $img, 1, "$d");
if ($plotmeta["subtitle"] != "") {
    $point = new pointobj();
    $point->setXY(80, 43);
    $point->draw($map, $tlayer, $img, 1, $plotmeta["subtitle"]);
}

$map->drawLabelCache($img);

$layer = $map->getLayerByName("logo");
$point = new pointobj();
$point->setXY(42, 32);
$point->draw($map, $layer, $img, 0, "");

if (in_array("nexrad", $layers) || in_array("nexrad_tc", $layers) || in_array("nexrad_tc6", $layers)) {
    $layer = $map->getLayerByName("n0r-ramp");
    $point = new pointobj();
    $point->setXY(($width - 80), 15);
    $point->draw($map, $layer, $img, 0, "");
}
if (in_array("n0q", $layers) || in_array("n0q_tc", $layers) || in_array("n0q_tc6", $layers) || in_array("hin0q", $layers) || in_array("akn0q", $layers) || in_array("prn0q", $layers)) {
    $layer = $map->getLayerByName("n0q-ramp");
    $point = new pointobj();
    $point->setXY(($width - 130), 18);
    $point->draw($map, $layer, $img, 0, "");
}

if (in_array("legend", $layers)) {
    $map->embedLegend($img);
}
//$map->drawLabelCache($img);
//$map->save("/tmp/test.map");

header("Content-type: image/png");
echo $img->getBytes();
