<?php
//TODO: deprecate this
require_once "../../../config/settings.inc.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/network.php";
require_once "../../../include/forms.php";
$nt = new NetworkTable("IA_RWIS");
$cities = $nt->table;

$gis = isset($_GET["gis"]) ? $_GET["gis"] : 'no';
$delim = isset($_GET["delim"]) ? $_GET["delim"] : ",";
$sample = isset($_GET["sample"]) ? $_GET["sample"] : "1min";
$what = isset($_GET["what"]) ? $_GET["what"] : 'dl';

$day1 = isset($_GET["day1"]) ? $_GET["day1"] : die("No day1 specified");
$day2 = isset($_GET["day2"]) ? $_GET["day2"] : die("No day2 specified");
$month1 = isset($_GET["month1"]) ? $_GET["month1"] : die("No month1 specified");
$month2 = isset($_GET["month2"]) ? $_GET["month2"] : die("No month2 specified");
$year1 = isset($_GET["year1"]) ? $_GET["year1"] : die("No year1 specified");
$year2 = isset($_GET["year2"]) ? $_GET["year2"] : die("No year2 specified");
$hour1 = isset($_GET["hour1"]) ? $_GET["hour1"] : die("No hour1 specified");
$hour2 = isset($_GET["hour2"]) ? $_GET["hour2"] : die("No hour2 specified");
$minute1 = isset($_GET["minute1"]) ? $_GET["minute1"] : die("No minute1 specified");
$minute2 = isset($_GET["minute2"]) ? $_GET["minute2"] : die("No minute2 specified");


$stations = $_GET["station"];
$selectAll = false;
foreach ($stations as $key => $value) {
    if ($value == "_ALL") {
        $selectAll = true;
        continue;
    }
    if (!array_key_exists($value, $cities)) {
        xssafe("<tag>");
    }
}


if ($selectAll) {
    $stations = array_keys($cities);
}

$stationSQL = "{". implode(",", $stations) . "}";

if (isset($_GET["day"]))
    die("Incorrect CGI param, use day1, day2");

$ts1 = mktime($hour1, $minute1, 0, $month1, $day1, $year1) or
    die("Invalid Date Format");
$ts2 = mktime($hour2, $minute2, 0, $month2, $day2, $year2) or
    die("Invalid Date Format");

if ($selectAll && $day1 != $day2)
    $ts2 = $ts1 + 86400;
$vars = array(
    "lane_id",
    "avg_speed",
    "avg_headway",
    "normal_vol",
    "long_vol",
    "occupancy"
);
$num_vars = count($vars);
if ($num_vars == 0)  die("You did not specify data");

$sqlStr = "SELECT station, ";
for ($i = 0; $i < $num_vars; $i++) {
    $sqlStr .= $vars[$i] . " as var" . $i . ", ";
}

$sqlTS1 = date("Y-m-d H:i", $ts1);
$sqlTS2 = date("Y-m-d H:i", $ts2);
$nicedate = date("Y-m-d", $ts1);

$d = array("space" => " ", "comma" => ",", "tab" => "\t");

$sqlStr .= "to_char(valid, 'YYYY-MM-DD HH24:MI') as dvalid from alldata_traffic";
$sqlStr .= " WHERE valid >= '" . $sqlTS1 . "' and valid <= '" . $sqlTS2 . "' ";
$sqlStr .= " and station = ANY($1) ORDER by valid ASC";

/**
 * Must handle different ideas for what to do...
 **/

if ($what == "download") {
    header("Content-type: application/octet-stream");
    header("Content-Disposition: attachment; filename=changeme.txt");
} else {
    header("Content-type: text/plain");
}

$connection = iemdb("rwis");

$query1 = "SET TIME ZONE 'UTC'";

$result = pg_exec($connection, $query1);
$stname = uniqid("st");
pg_prepare($connection, $stname, $sqlStr);
$rs = pg_execute($connection, $stname, array($stationSQL));

if ($gis == "yes") {
    echo "station,station_name,lat,lon,valid(GMT),";
} else {
    echo "station,station_name,valid(GMT),";
}
for ($j = 0; $j < $num_vars; $j++) {
    echo $vars[$j] . $d[$delim];
    if ($vars[$j] == "ca1") echo "ca1code" . $d[$delim];
    if ($vars[$j] == "ca2") echo "ca2code" . $d[$delim];
    if ($vars[$j] == "ca3") echo "ca3code" . $d[$delim];
}
echo "\n";

for ($i = 0; $row = pg_fetch_array($rs); $i++) {
    $sid = $row["station"];
    echo $sid . $d[$delim] . $cities[$sid]["name"];
    if ($gis == "yes") {
        echo  $d[$delim] . $cities[$sid]["lat"] . $d[$delim] .  $cities[$sid]["lon"];
    }
    echo $d[$delim] . $row["dvalid"] . $d[$delim];
    for ($j = 0; $j < $num_vars; $j++) {
        echo $row["var" . $j] . $d[$delim];
    }
    echo "\n";
}
