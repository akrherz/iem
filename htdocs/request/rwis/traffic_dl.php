<?php
//TODO: deprecate this
require_once "../../../config/settings.inc.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/network.php";
require_once "../../../include/forms.php";
$nt = new NetworkTable("IA_RWIS");
$cities = $nt->table;

$gis = isset($_GET["gis"]) ? xssafe($_GET["gis"]) : 'no';
$delim = isset($_GET["delim"]) ? xssafe($_GET["delim"]) : "comma";
$sample = isset($_GET["sample"]) ? xssafe($_GET["sample"]) : "1min";
$what = isset($_GET["what"]) ? xssafe($_GET["what"]) : 'dl';

$day1 = isset($_GET["day1"]) ? xssafe($_GET["day1"]) : die("No day1 specified");
$day2 = isset($_GET["day2"]) ? xssafe($_GET["day2"]) : die("No day2 specified");
$month1 = isset($_GET["month1"]) ? xssafe($_GET["month1"]) : die("No month1 specified");
$month2 = isset($_GET["month2"]) ? xssafe($_GET["month2"]) : die("No month2 specified");
$year1 = isset($_GET["year1"]) ? xssafe($_GET["year1"]) : die("No year1 specified");
$year2 = isset($_GET["year2"]) ? xssafe($_GET["year2"]) : die("No year2 specified");
$hour1 = isset($_GET["hour1"]) ? xssafe($_GET["hour1"]) : die("No hour1 specified");
$hour2 = isset($_GET["hour2"]) ? xssafe($_GET["hour2"]) : die("No hour2 specified");
$minute1 = isset($_GET["minute1"]) ? xssafe($_GET["minute1"]) : die("No minute1 specified");
$minute2 = isset($_GET["minute2"]) ? xssafe($_GET["minute2"]) : die("No minute2 specified");

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

$sqlStr = "SELECT station, ";
for ($i = 0; $i < $num_vars; $i++) {
    $sqlStr .= $vars[$i] . " as var{$i}, ";
}

$sqlTS1 = date("Y-m-d H:i", $ts1);
$sqlTS2 = date("Y-m-d H:i", $ts2);
$nicedate = date("Y-m-d", $ts1);

$d = array("space" => " ", "comma" => ",", "tab" => "\t");
if (!array_key_exists($delim, $d)) {
    xssafe("<tag>");
}

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
$rs = pg_prepare($connection, $stname, $sqlStr);
if ($rs === FALSE) {
    http_send_status(503);
    die("Database failure");
}
$rs = pg_execute($connection, $stname, array($stationSQL));

$dd = $d[$delim];

if ($gis == "yes") {
    echo "station{$dd}station_name{$dd}lat{$dd}lon{$dd}valid(GMT){$dd}";
} else {
    echo "station{$dd}station_name{$dd}valid(GMT){$dd}";
}
for ($j = 0; $j < $num_vars; $j++) {
    echo $vars[$j] . $dd;
    if ($vars[$j] == "ca1") echo "ca1code" . $dd;
    if ($vars[$j] == "ca2") echo "ca2code" . $dd;
    if ($vars[$j] == "ca3") echo "ca3code" . $dd;
}
echo "\n";

while ($row = pg_fetch_assoc($rs)) {
    $sid = $row["station"];
    echo $sid . $dd . $cities[$sid]["name"];
    if ($gis == "yes") {
        echo $dd . $cities[$sid]["lat"] . $dd .  $cities[$sid]["lon"];
    }
    echo $dd . $row["dvalid"] . $dd;
    for ($j = 0; $j < $num_vars; $j++) {
        echo $row["var{$j}"] . $dd;
    }
    echo "\n";
}
