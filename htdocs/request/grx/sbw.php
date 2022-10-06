<?php
/* 
 * Generate a placefile of SBWs valid at a given time for a given WFO
 */
require_once "../../../config/settings.inc.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/vtec.php";
$connect = iemdb("postgis");
pg_query($connect, "SET TIME ZONE 'UTC'");

$year = isset($_GET["year"]) ? intval($_GET["year"]) : 2008;
$month = isset($_GET["month"]) ? intval($_GET["month"]) : 1;
$day = isset($_GET["day"]) ? intval($_GET["day"]) : 8;
$hour = isset($_GET["hour"]) ? intval($_GET["hour"]) : 10;
$minute = isset($_GET["minute"]) ? intval($_GET["minute"]) : 0;
$ts = gmmktime($hour, $minute, 0, $month, $day, $year);
$wfo = isset($_GET["wfo"]) ? substr($_GET["wfo"], 0, 3) : "MPX";

$rs = pg_prepare($connect, "SELECT", "SELECT *, ST_AsText(geom) as g, 
           round(ST_area(ST_transform(geom,2163)) / 1000000.0) as psize
           from sbw_$year 
           WHERE wfo = $1 and issue <= $2 and expire > $2
           and status = 'NEW'");

$result = pg_execute(
    $connect,
    "SELECT",
    array($wfo, gmdate("Y-m-d H:i", $ts))
);

$fp = sprintf("%s-%s.txt", $wfo, gmdate("YmdHi", $ts));
header("Content-type: application/octet-stream");
header("Content-Disposition: attachment; filename=$fp");
echo "Refresh: 99999\n";
echo "Threshold: 999\n";
echo sprintf("Title: $wfo SBW @ %s UTC\n", gmdate("d M Y H:i", $ts));

for ($i = 0; $row = pg_fetch_array($result); $i++) {
    $geom = $row["g"];
    $geom = str_replace("MULTIPOLYGON(((", "", $geom);
    $geom = str_replace(")))", "", $geom);
    $tokens = preg_split("/,/", $geom);
    $phenomena = $row['phenomena'];
    $significance = $row['significance'];
    $issue = strtotime($row["issue"]);
    $expire = strtotime($row["expire"]);
    $lbl = $vtec_phenomena[$phenomena] . " " . $vtec_significance[$significance] . " " .
        $row["eventid"] . "\\nIssue: " . gmdate("Hi", $issue) . "Z Expire: " .
        gmdate("Hi", $expire) . "Z";
    echo "\n;";

    if ($row["phenomena"] == "SV") {
        $c = "255 255 0 255";
    } else {
        $c = "255 0 0 255";
    }
    echo "Color: $c\n";
    echo "Line: 3, 0, \"$lbl\"\n";
    $first = true;
    foreach ($tokens as $token) {

        $parts = preg_split("/ /", $token);
        $extra = "";
        if ($first) {
            $extra = $c;
            $first = false;
        }
        echo sprintf("%.4f, %.4f\n", $parts[1], $parts[0]);
    }
    echo "End:\n\n";
}
