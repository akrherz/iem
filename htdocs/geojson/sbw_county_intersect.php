<?php
header("Content-type: application/vnd.geo+json");
require_once "../../config/settings.inc.php";
require_once "../../include/database.inc.php";
require_once "../../include/forms.php";
$connect = iemdb("postgis");

$year = get_int404("year", 2006);
$wfo = isset($_GET["wfo"]) ? xssafe($_GET["wfo"]) : "MPX";
if (strlen($wfo) > 3) {
    $wfo = substr($wfo, 1, 3);
}
$eventid = get_int404("eventid", 103);
$phenomena = isset($_GET["phenomena"]) ? substr(xssafe($_GET["phenomena"]), 0, 2) : "SV";
$significance = isset($_GET["significance"]) ? substr(xssafe($_GET["significance"]), 0, 1) : "W";

$sql = <<<EOF
    WITH stormbased as (SELECT geom from sbw_$year where wfo = '$wfo'
        and eventid = $eventid and significance = '$significance'
        and phenomena = '$phenomena' and status = 'NEW'),
    countybased as (SELECT ST_Union(u.geom) as geom from
        warnings_$year w JOIN ugcs u on (u.gid = w.gid)
        WHERE w.wfo = '$wfo' and eventid = $eventid and
        significance = '$significance' and phenomena = '$phenomena')

    SELECT ST_asgeojson(geo) as geojson, ST_Length(ST_transform(geo,9311)) as sz from
        (SELECT ST_SetSRID(ST_intersection(
          ST_buffer(ST_exteriorring(ST_geometryn(ST_multi(c.geom),1)),0.02),
          ST_exteriorring(ST_geometryn(ST_multi(s.geom),1))
            ), 4326) as geo
    from stormbased s, countybased c) as foo
EOF;
$rs = pg_exec($connect, $sql);


$ar = array(
    "type" => "FeatureCollection",
    "features" => array()
);
$reps = array();
$subs = array();

for ($i = 0; $row = pg_fetch_assoc($rs); $i++) {

    $reps[] = "\"REPLACEME$i\"";
    $subs[] = $row["geojson"];

    $z = array(
        "type" => "Feature", "id" => $i,
        "properties" => array(
            "sz" => $row["sz"]
        ),
        "geometry" => "REPLACEME$i"
    );

    $ar["features"][] = $z;
}
echo str_replace($reps, $subs, json_encode($ar));
