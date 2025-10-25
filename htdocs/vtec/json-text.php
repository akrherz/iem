<?php
// Giveme JSON data for zones affected by warning
// 4 March 2024: Still being actively used, sigh
require_once '../../config/settings.inc.php';
require_once "../../include/database.inc.php";
require_once "../../include/forms.php";
require_once "../../include/mlib.php";

$connect = iemdb("postgis");
pg_exec($connect, "SET TIME ZONE 'UTC'");

$year = get_int404("year", 2006);
if ($year == 0) die("ERROR: invalid \$year set");
$wfo = get_str404("wfo", "MPX", 3);
$eventid = get_int404("eventid", 103);
$phenomena = get_str404("phenomena", "SV", 2);
$significance = get_str404("significance", "W", 1);
$lastsvs = get_str404("lastsvs", 'n');

$stname = iem_pg_prepare(
    $connect,
    "SELECT array_to_json(product_ids) as ja ".
    "from warnings WHERE vtec_year = $1 and wfo = $2 and ".
    "phenomena = $3 and eventid = $4 and significance = $5 ".
    "ORDER by cardinality(product_ids) DESC LIMIT 1"
);
$rs = pg_execute($connect, $stname, Array($year, $wfo, $phenomena, $eventid, $significance));

$ar = array("data" => array());
if (pg_num_rows($rs) > 0) {
    $row = pg_fetch_assoc($rs, 0);
    $product_ids = json_decode($row["ja"]);

    $z = array();
    $z["id"] = 1;
    $report = file_get_contents("{$INTERNAL_BASEURL}/api/1/nwstext/". $product_ids[0]);
    $z["report"] = preg_replace("/\001/", "",
        preg_replace("/\r\r\n/", "\n", $report));
    $z["svs"] = array();
    $lsvs = "";
    for ($i=1; $i < sizeof($product_ids); $i++) {
        $report = file_get_contents("{$INTERNAL_BASEURL}/api/1/nwstext/". $product_ids[$i]);
        $lsvs = preg_replace("/\001/", "", htmlspecialchars($report));
        $z["svs"][] = preg_replace("/\r\r\n/", "\n", $lsvs);
    }
    if ($lastsvs == "y") {
        $z["svs"] = preg_replace("/\r\r\n/", "\n", $lsvs);
    }
    $ar["data"][] = $z;
}
header("Content-type: application/json");
echo json_encode($ar);
