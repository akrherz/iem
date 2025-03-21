<?php
header("Content-type: text/plain");

/*
 * Iowa DOT provided state road conditions
 */
require_once "../../../config/settings.inc.php";
require_once "../../../include/memcache.php";

// Try to get it from memcached
$memcache = MemcacheSingleton::getInstance();
$val = $memcache->get("/request/grx/roadcond.php");
if ($val) {
    die($val);
}
ob_start();

require_once "../../../include/database.inc.php";
$conn = iemdb('postgis');

$colors = array(
    0 => "255 255 255", // normal
    76 => "255 255 255",

    1 => "0 204 0", // wet

    3 => "240 240 0", // Frost
    7 => "240 240 0",
    11 => "240 240 0",

    15 => "255 197 197", // Partially Covered
    27 => "255 197 197",
    56 => "255 197 197",

    19 => "254 51 153", // Mostly Covered
    31 => "254 51 153",
    60 => "254 51 153",

    23 => "181 0 181", // Completely Covered
    35 => "181 0 181",
    64 => "181 0 181",

    39 => "153 255 255", // PC Snow

    43 => "0 153 254", // MC Snow

    47 => "0 0 158", // CC Snow

    51 => "232 95 1", // Travel Advisory

    86 => "125 0 0" // Closed
);


echo "Threshold: 999
Title: IEM Delivered Iowa Road Conditions
Refresh: 5
";

$rs = pg_query($conn, "SELECT ST_astext(ST_transform(simple_geom,4326)) as t, ". 
        "* from roads_current r, roads_base b, roads_conditions c ".
        "WHERE r.segid = b.segid and r.cond_code = c.code ".
        "and b.geom is not null ORDER by type DESC");

while ($row = pg_fetch_assoc($rs)) {
    $meat = str_replace("MULTILINESTRING((", "", $row["t"]);
    $meat = str_replace("))", "", $meat);
    $segments = explode("),(", $meat);
    $valid = strtotime(substr($row["valid"], 0, 16));
    $color = "255 255 255";
    if (array_key_exists($row["cond_code"], $colors)) {
        $color = $colors[$row["cond_code"]];
    }
    echo "Color: {$color}\n";
    foreach ($segments as $q => $seg) {
        echo "Line: 4, 0, " . $row["major"] . " :: " . $row["minor"]  . "\\nReport: " . $row["raw"] . "\\nTime: " . date('j M Y g:i A', $valid) . "\n";
        $tokens = explode(",", $seg);
        foreach ($tokens as $p => $s) {
            $t = explode(" ", $s);
            echo sprintf("  %.5f,%.5f", $t[1], $t[0]) . "\n";
        }
        echo "End:\n";
    }
}

$memcache->set("/request/grx/roadcond.php", ob_get_contents(), 300);
ob_end_flush();
