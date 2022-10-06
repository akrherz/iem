<?php
/* Giveme JSON data for zones affected by warning 
 * This is used by some random AWS EC2 host to get lastsvs=y 
 * 25 May 2021: still used
 */
require_once '../../config/settings.inc.php';
require_once "../../include/database.inc.php";
require_once "../../include/forms.php";

$connect = iemdb("postgis");
pg_exec($connect, "SET TIME ZONE 'UTC'");

$year = get_int404("year", 2006);
if ($year == 0) die("ERROR: invalid \$year set");
$wfo = isset($_GET["wfo"]) ? substr(xssafe($_GET["wfo"]), 0, 3) : "MPX";
$eventid = get_int404("eventid", 103);
$phenomena = isset($_GET["phenomena"]) ? substr(xssafe($_GET["phenomena"]), 0, 2) : "SV";
$significance = isset($_GET["significance"]) ? substr(xssafe($_GET["significance"]), 0, 1) : "W";
$lastsvs = isset($_GET["lastsvs"]) ? xssafe($_GET["lastsvs"]) : 'n';

$sql = "SELECT replace(report,'\001','') as report, 
               replace(svs,'\001','') as svs
        from warnings_$year w WHERE w.wfo = '$wfo' and 
        w.phenomena = '$phenomena' and w.eventid = $eventid and 
        w.significance = '$significance' ORDER by length(svs) DESC LIMIT 1";


$result = pg_exec($connect, $sql);

$ar = array("data" => array());
for ($i = 0; $row  = pg_fetch_array($result); $i++) {
    $z = array();
    $z["id"] = $i + 1;
    $z["report"] = preg_replace("/\r\r\n/", "\n", $row["report"]);
    $z["svs"] = array();
    $tokens = @explode('__', $row["svs"]);
    $lsvs = "";
    foreach ($tokens as $key => $val) {
        if ($val == "") continue;
        $lsvs = htmlspecialchars($val);
        $z["svs"][] = preg_replace("/\r\r\n/", "\n", $lsvs);
    }
    if ($lastsvs == "y") {
        $z["svs"] = preg_replace("/\r\r\n/", "\n", $lsvs);
    }
    $ar["data"][] = $z;
}

header("Content-type: application/json");
echo json_encode($ar);
