<?php
require_once "../../../config/settings.inc.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/network.php";
require_once "../../../include/forms.php";
$nt = new NetworkTable("IA_ASOS");

$skycover = array(
    0 => "NOREPORT",
    1 => "SCATTERED",
    2 => "BROKEN",
    4 => "OVERCAST",
    8 => "OBSCURATION",
    16 => "UNKNOWN",
    17 => "OBSCURATION",
    18 => "OBSCURATION",
    20 => "OBSCURATION",
    32 => "INDEFINITE",
    64 => "CLEAR",
    128 => "FEW",
    255 => "MISSING"
);

$gis = get_str404("gis", 'no');
$delim = get_str404("delim", ",");
$sample = get_str404("sample", "1min");
$what = get_str404("what", 'dl');
$tz = get_str404("tz", 'UTC');

$day1 = get_int404("day1", 1);
$day2 = get_int404("day2", 1);
$month1 = get_int404("month1", 1);
$month2 = get_int404("month2", 2);
$year1 = get_int404("year1", 2020);
$year2 = get_int404("year2", 2020);
$hour1 = get_int404("hour1", 0);
$hour2 = get_int404("hour2", 0);
$minute1 = get_int404("minute1", 0);
$minute2 = get_int404("minute2", 0);
$vars = array_key_exists("vars", $_GET) ? $_GET["vars"] : ["tmpf"];

$stations = array_key_exists("station", $_GET) ? $_GET["station"] : ["BNW"];
$selectAll = false;
foreach ($stations as $key => $value) {
    if ($value === "_ALL") {
        $selectAll = true;
        continue;
    }
    if (strlen($value) > 4 && !array_key_exists($value, $nt->table)) {
        xssafe("<tag>");
    }
}
if ($selectAll) {
    $stations = array_keys($nt->table);
}


$ts1 = mktime($hour1, $minute1, 0, $month1, $day1, $year1);
$ts2 = mktime($hour2, $minute2, 0, $month2, $day2, $year2);

if ($selectAll && $day1 != $day2)
    $ts2 = $ts1 + 86400;

$num_vars = count($vars);
if ($num_vars == 0)  die("You did not specify data");

$sqlStr = "SELECT station, ";
for ($i = 0; $i < $num_vars; $i++) {
    $sqlStr .= xssafe($vars[$i]) . " as var{$i}, ";
}

$sqlTS1 = date("Y-m-d H:i", $ts1);
$sqlTS2 = date("Y-m-d H:i", $ts2);
$nicedate = date("Y-m-d", $ts1);

$sampleStr = array(
    "1min" => "1",
    "5min" => "5",
    "10min" => "10",
    "20min" => "20",
    "1hour" => "60"
);

$d = array("space" => " ", "comma" => ",", "tab" => "\t");

$sqlStr .= "to_char(valid, 'YYYY-MM-DD HH24:MI') as dvalid from alldata ";
$sqlStr .= " WHERE valid >= '" . $sqlTS1 . "' and valid <= '" . $sqlTS2 . "' ";
$sqlStr .= " and extract(minute from valid)::int % " . $sampleStr[$sample] . " = 0 ";
$sqlStr .= " and station = ANY($1) ORDER by valid ASC";

if ($what == "download") {
    header("Content-type: application/octet-stream");
    header("Content-Disposition: attachment; filename=changeme.txt");
} else {
    header("Content-type: text/plain");
}

$conn = iemdb("awos");

$tzn = "local";
if ($tz == "UTC") {
    $tzn = "UTC";
    $result = pg_exec($conn, "SET TIME ZONE 'UTC'");
}

$stname = iem_pg_prepare($conn, $sqlStr);
$rs = pg_execute($conn, $stname, Array("{ " . implode(",", $stations) . " }"));

if ($gis == "yes") {
    echo "station,station_name,lat,lon,valid($tzn),";
} else {
    echo "station,station_name,valid($tzn),";
}
for ($j = 0; $j < $num_vars; $j++) {
    echo $vars[$j] . $d[$delim];
    if ($vars[$j] == "ca1") echo "ca1code" . $d[$delim];
    if ($vars[$j] == "ca2") echo "ca2code" . $d[$delim];
    if ($vars[$j] == "ca3") echo "ca3code" . $d[$delim];
}
echo "\n";

for ($i = 0; $row = pg_fetch_assoc($rs); $i++) {
    $sid = $row["station"];
    echo $sid . $d[$delim] . $nt->table[$sid]["name"];
    if ($gis == "yes") {
        echo  $d[$delim] . $nt->table[$sid]["lat"] . $d[$delim] .  $nt->table[$sid]["lon"];
    }
    echo $d[$delim] . $row["dvalid"] . $d[$delim];
    for ($j = 0; $j < $num_vars; $j++) {
        echo $row["var" . $j] . $d[$delim];
        if ($vars[$j] == "ca1") echo $skycover[$row["var" . $j]] . $d[$delim];
        if ($vars[$j] == "ca2") echo $skycover[$row["var" . $j]] . $d[$delim];
        if ($vars[$j] == "ca3") echo $skycover[$row["var" . $j]] . $d[$delim];
    }
    echo "\n";
}
