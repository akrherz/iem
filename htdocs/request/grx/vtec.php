<?php
require_once "../../../config/settings.inc.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/reference.php";
require_once "../../../include/forms.php";
$connect = iemdb("postgis");

$year = get_int404("year", 2006);
if ($year < 2002) die("invalid year specified!");

$wfo = substr(get_str404("wfo", "MPX"), 0, 4);
if (strlen($wfo) > 3) {
    $wfo = substr($wfo, 1, 3);
}
$eventid = get_int404("eventid", 103);
$phenomena = substr(get_str404("phenomena", "SV"), 0, 2);
$significance = substr(get_str404("significance", "W"), 0, 1);

$stname = iem_pg_prepare($connect, "SELECT eventid, phenomena, ".
        "significance, ST_AsText(geom) as g ".
        "from sbw ".
        "WHERE vtec_year = $5 and wfo = $1 and phenomena = $2 and ".
        "eventid = $3 and significance = $4 ".
        "and status = 'NEW'");
$result = pg_execute(
    $connect,
    $stname,
    array($wfo, $phenomena, $eventid, $significance, $year)
);
if (pg_num_rows($result) <= 0) {
    $stname = iem_pg_prepare($connect, "SELECT eventid, phenomena, ".
        "significance, ST_astext(u.geom) as g ".
        "from warnings w JOIN ugcs u on (u.gid = w.gid) ".
        "WHERE w.vtec_year = $5 and w.wfo = $1 and phenomena = $2 and ".
        "eventid = $3 and significance = $4 ");

    $result = pg_execute(
        $connect,
        $stname,
        array($wfo, $phenomena, $eventid, $significance, $year)
    );
}
$fp = sprintf("%s-%s-%s-%s.txt", $wfo, $phenomena, $significance, $eventid);

header("Content-type: application/octet-stream");
header("Content-Disposition: attachment; filename=$fp");

echo "Refresh: 99999\n";
echo "Threshold: 999\n";
echo "Title: VTEC $wfo {$phenomena}.{$significance} $eventid\n";

while ($row = pg_fetch_assoc($result)) {
    $geom = $row["g"];
    $geom = str_replace("MULTIPOLYGON(((", "", $geom);
    $geom = str_replace(")))", "", $geom);
    $tokens = preg_split("/,/", $geom);
    $phenomena = $row['phenomena'];
    $significance = $row['significance'];
    echo "\n;" . $reference["vtec_phenomena"][$phenomena] . " " . $reference["vtec_significance"][$significance] . " " . $row["eventid"] . "\n";

    if ($row["phenomena"] == "SV") {
        $c = "255 255 0 255";
    } else {
        $c = "255 0 0 255";
    }
    echo "Color: $c\n";
    echo "Line: 3, 0, \"\"\n";
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
