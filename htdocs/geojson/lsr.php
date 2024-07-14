<?php
//Generate GeoJSON LSR information for a period of choice
header("Content-type: application/vnd.geo+json");
require_once "../../config/settings.inc.php";
require_once "../../include/database.inc.php";
require_once "../../include/vtec.php";
require_once "../../include/forms.php";
$postgis = iemdb("postgis");

function toTime($s)
{
    return mktime(
        intval(substr($s, 8, 2)),
        intval(substr($s, 10, 2)),
        intval(substr($s, 12, 2)),
        intval(substr($s, 4, 2)),
        intval(substr($s, 6, 2)),
        intval(substr($s, 0, 4))
    );
}

$rs = pg_query($postgis, "SET TIME ZONE 'UTC'");

if (isset($_REQUEST["phenomena"])) {
    $year = isset($_GET["year"]) ? intval($_GET["year"]) : 2006;
    $wfo = isset($_GET["wfo"]) ? substr($_GET["wfo"], 0, 3) : "MPX";
    $eventid = get_int404("eventid", 103);
    $phenomena = isset($_GET["phenomena"]) ? substr($_GET["phenomena"], 0, 2) : "SV";
    $significance = isset($_GET["significance"]) ?
        substr($_GET["significance"], 0, 1) : "W";

    /* Now we fetch warning and perhaps polygon */
    $rs = pg_prepare($postgis, "SELECT", "SELECT l.*, 
          to_char(valid, 'YYYY-MM-DDThh24:MI:SSZ') as iso_valid,
              ST_x(l.geom) as lon, ST_y(l.geom) as lat
           from sbw_$year w, lsrs l
           WHERE w.wfo = $1 and w.phenomena = $2 and 
           w.eventid = $3 and w.significance = $4
           and w.geom && l.geom and l.valid BETWEEN w.issue and w.expire
           and w.status = 'NEW'");
    $rs = pg_execute($postgis, "SELECT", array(
        $wfo, $phenomena,
        $eventid, $significance
    ));
} else if (isset($_GET["states"]) && $_GET["states"] != "") {
    $states = explode(",", xssafe($_GET["states"]));
    $sts = isset($_REQUEST["sts"]) ? toTime($_REQUEST["sts"]) : die("sts not defined");
    $ets = isset($_REQUEST["ets"]) ? toTime($_REQUEST["ets"]) : die("ets not defined");
    $stateList = implode("','", $states);
    $str_state_list = "and s.state_abbr in ('$stateList')";
    $rs = pg_prepare($postgis, "SELECT", "SELECT distinct l.*, 
        to_char(valid, 'YYYY-MM-DDThh24:MI:SSZ') as iso_valid,
        ST_x(l.geom) as lon, ST_y(l.geom) as lat 
          FROM lsrs l, states s WHERE
          valid BETWEEN $1 and $2 $str_state_list
          and ST_Intersects(l.geom, s.the_geom)
          LIMIT 10000");

    $rs = pg_execute($postgis, "SELECT", array(
        date("Y-m-d H:i", $sts),
        date("Y-m-d H:i", $ets)
    ));

} else {
    /* Look for calling values */
    $wfos = isset($_REQUEST["wfos"]) ? explode(",", $_REQUEST["wfos"]) : array();
    $sts = isset($_REQUEST["sts"]) ? toTime($_REQUEST["sts"]) : die("sts not defined");
    $ets = isset($_REQUEST["ets"]) ? toTime($_REQUEST["ets"]) : die("ets not defined");
    $wfoList = implode("','", $wfos);
    $str_wfo_list = "and wfo in ('$wfoList')";
    if ($wfoList == "") {
        $str_wfo_list = "";
    }

    $rs = pg_prepare($postgis, "SELECT", "SELECT distinct wfo, type, magnitude,
        county, typetext, state, remark, city, source, unit,
        to_char(valid, 'YYYY-MM-DDThh24:MI:SSZ') as iso_valid,
        ST_x(geom) as lon, ST_y(geom) as lat 
          FROM lsrs WHERE
          valid BETWEEN $1 and $2 $str_wfo_list
          LIMIT 10000");

    $rs = pg_execute($postgis, "SELECT", array(
        date("Y-m-d H:i", $sts),
        date("Y-m-d H:i", $ets)
    ));
}

$ar = array(
    "type" => "FeatureCollection",
    "features" => array()
);

for ($i = 0; $row = pg_fetch_assoc($rs); $i++) {
    $lon = floatval($row["lon"]);
    $lat = floatval($row["lat"]);
    $wfo = $row["wfo"];
    $products = "N/A";
    if (isset($_GET["inc_ap"]) && $_GET["inc_ap"] == "yes") {
        /* Lets go looking for warnings for this particular LSR, fast please */
        $sql = sprintf(
            "SELECT distinct phenomena, significance, eventid
        from sbw_%s
        WHERE wfo = '%s' and issue <= '%s' 
        and issue > '%s'::timestamp - '7 days'::interval and expire > '%s'
        and ST_POINT(%s, %s, 4326) && geom
        and ST_contains(geom, ST_POINT(%s, %s, 4326))",
            substr($row["valid"], 0, 4),
            $wfo,
            $row["valid"],
            $row['valid'],
            $row["valid"],
            $lon,
            $lat,
            $lon,
            $lat
        );
        $rs2 = pg_query($postgis, $sql);
        $products = "";
        for ($j = 0; $row2 = pg_fetch_array($rs2); $j++) {
            $vtecurl = sprintf(
                "%s/vtec/#%s-O-NEW-K%s-%s-%s-%04d",
                ROOTURL,
                substr($row["valid"], 0, 4),
                $wfo,
                $row2["phenomena"],
                $row2["significance"],
                $row2["eventid"]
            );
            $products .= sprintf(
                "<a href='%s'>%s %s %s</a> &nbsp; ",
                $vtecurl,
                $vtec_phenomena[$row2["phenomena"]],
                $vtec_significance[$row2["significance"]],
                $row2["eventid"]
            );
        }
        if ($products == "") {
            $products = "None";
        }
    }
    $magnitude = $row["magnitude"];
    if (
        $row["type"] == 'S' && is_numeric($row["magnitude"]) &&
        floatval($row["magnitude"] > 0)
    ) {
        $magnitude = sprintf("%.1f", floatval($row["magnitude"]));
    }
    if (
        $row["type"] == 'R' && is_numeric($row["magnitude"]) &&
        floatval($row["magnitude"] > 0)
    ) {
        $magnitude = sprintf("%.2f", floatval($row["magnitude"]));
    }

    $z = array(
        "type" => "Feature", "id" => $i,
        "properties" => array(
            "magnitude" => (is_null($magnitude)) ? "" : $magnitude,
            "wfo"       => $row["wfo"],
            "valid"     => $row["iso_valid"],
            "type"      => $row["type"],
            "county"    => $row["county"],
            "typetext"  => $row["typetext"],
            "st"        => $row["state"],
            "remark"    => $row["remark"],
            "city"      => $row["city"],
            "source"    => $row["source"],
            "unit" => $row["unit"],
            "lat"      => $lat,
            "lon"      => $lon,
            "prodlinks" => $products,
        ),
        "geometry" => array(
            "type" => "Point",
            "coordinates" => array($lon, $lat)
        )
    );
    $ar["features"][] = $z;
}

echo json_encode($ar);
