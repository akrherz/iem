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
$wfo = isset($_GET["wfo"]) ? substr(xssafe($_GET["wfo"]), 0, 3) : "MPX";
$eventid = get_int404("eventid", 103);
$phenomena = isset($_GET["phenomena"]) ? substr(xssafe($_GET["phenomena"]), 0, 2) : "SV";
$significance = isset($_GET["significance"]) ? substr(xssafe($_GET["significance"]), 0, 1) : "W";
$lastsvs = isset($_GET["lastsvs"]) ? xssafe($_GET["lastsvs"]) : 'n';

$rs = pg_prepare(
    $connect,
    "SELECT",
    "SELECT array_to_json(product_ids) as ja ".
    "from warnings_$year WHERE wfo = $1 and ". 
    "phenomena = $2 and eventid = $3 and significance = $4 ".
    "ORDER by cardinality(product_ids) DESC LIMIT 1"
);
$rs = pg_execute($connect, "SELECT", Array($wfo, $phenomena, $eventid, $significance));

$ar = array("data" => array());
$row = pg_fetch_assoc($rs, 0);
$product_ids = json_decode($row["ja"]);

$z = array();
$z["id"] = 1;
$report = file_get_contents("http://iem.local/api/1/nwstext/". $product_ids[0]);
$z["report"] = preg_replace("/\001/", "",
    preg_replace("/\r\r\n/", "\n", $report));
$z["svs"] = array();
$lsvs = "";
for ($i=1; $i < sizeof($product_ids); $i++) {
    $report = file_get_contents("http://iem.local/api/1/nwstext/". $product_ids[$i]);
    $lsvs = preg_replace("/\001/", "", htmlspecialchars($report));
    $z["svs"][] = preg_replace("/\r\r\n/", "\n", $lsvs);
}
if ($lastsvs == "y") {
    $z["svs"] = preg_replace("/\r\r\n/", "\n", $lsvs);
}
$ar["data"][] = $z;

header("Content-type: application/json");
echo json_encode($ar);
