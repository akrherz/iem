<?php
// Big downloads exceed 30 second limit.
set_time_limit(300);
require_once "../../../config/settings.inc.php";
// This script can be too intensive and jam up php-fpm, so we throttle
require_once "../../../include/throttle.php";
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
    17 => "OBSCURATION",
    18 => "OBSCURATION",
    20 => "OBSCURATION",
    32 => "INDEFINITE",
    64 => "CLEAR",
    128 => "FEW",
    255 => "MISSING"
);

if (! isset($_GET["station"])) {
    xssafe("</script>");
}
$gis = isset($_GET["gis"]) ? xssafe($_GET["gis"]) : 'no';
$delim = isset($_GET["delim"]) ? xssafe($_GET["delim"]) : "comma";
$sample = isset($_GET["sample"]) ? xssafe($_GET["sample"]) : "1min";
$what = isset($_GET["what"]) ? xssafe($_GET["what"]) : 'dl';

$day1 = get_int404("day1");
if (is_null($day1)) die("No day1 specified");
$day2 = isset($_GET["day2"]) ? xssafe($_GET["day2"]) : die("No day2 specified");
$month1 = isset($_GET["month1"]) ? xssafe($_GET["month1"]) : die("No month specified");
$month2 = isset($_GET["month2"]) ? xssafe($_GET["month2"]) : die("No month specified");
$year1 = isset($_GET["year1"]) ? xssafe($_GET["year1"]) : die("No year1 specified");
$year2 = isset($_GET["year2"]) ? xssafe($_GET["year2"]) : die("No year2 specified");
$hour1 = isset($_GET["hour1"]) ? xssafe($_GET["hour1"]) : die("No hour1 specified");
$hour2 = isset($_GET["hour2"]) ? xssafe($_GET["hour2"]) : die("No hour2 specified");
$minute1 = isset($_GET["minute1"]) ? xssafe($_GET["minute1"]) : die("No minute1 specified");
$minute2 = isset($_GET["minute2"]) ? xssafe($_GET["minute2"]) : die("No minute2 specified");
$vars = isset($_GET["vars"]) ? $_GET["vars"] : die("No vars specified");
$tz = isset($_REQUEST['tz']) ? $_REQUEST['tz'] : 'UTC';

$stations = $_GET["station"];
$stationString = "(";
foreach ($stations as $key => $value) {
    $sid = trim(substr($value, 0, 4));
    $stationString .= " '{$sid}',";
    $nt->loadStation($sid);
}
if ($stationString == "("){
    die("no station set.");
}
$cities = $nt->table;
$stationString = substr($stationString, 0, -1);
$stationString .= ")";

if (isset($_GET["day"]))
    die("Incorrect CGI param, use day1, day2");

$ts1 = new DateTime("{$year1}-{$month1}-{$day1} {$hour1}:{$minute1}");
$ts2 = new DateTime("{$year2}-{$month2}-{$day2} {$hour2}:{$minute2}");

$num_vars = count($vars);
if ($num_vars == 0)  die("You did not specify data");

$sqlStr = "SELECT station, ";
for ($i = 0; $i < $num_vars; $i++) {
    $sqlStr .= substr($vars[$i], 0, 11) . " as var" . $i . ", ";
}

$sqlTS1 = $ts1->format("Y-m-d H:i");
$sqlTS2 = $ts2->format("Y-m-d H:i");
$table = "alldata_1minute";
$nicedate = $ts1->format("Y-m-d");

$sampleStr = array(
    "1min" => "1",
    "5min" => "5",
    "10min" => "10",
    "20min" => "20",
    "1hour" => "60"
);

$d = array("space" => " ", "comma" => ",", "tab" => "\t", "," => ",");

$sqlStr .= "to_char(valid, 'YYYY-MM-DD HH24:MI') as dvalid from " . $table;
$sqlStr .= " WHERE valid >= '" . $sqlTS1 . "' and valid <= '" . $sqlTS2 . "' ";
$sqlStr .= " and extract(minute from valid)::int % " . $sampleStr[$sample] . " = 0 ";
$sqlStr .= " and station IN " . $stationString . " ORDER by valid ASC";

/**
 * Must handle different ideas for what to do...
 **/
if ($what == "download") {
    header("Content-type: application/octet-stream");
    header("Content-Disposition: attachment; filename=changeme.txt");
} else {
    header("Content-type: text/plain");
}

/* Database Connection */
$dbconn = iemdb("asos1min");

if ($tz == 'UTC') {
    pg_exec($dbconn, "SET TIME ZONE 'UTC'");
}

pg_prepare($dbconn, "SELECT", $sqlStr);
$rs = pg_execute($dbconn, "SELECT", array());
pg_close($dbconn);

if ($gis == "yes") {
    echo "station,station_name,lat,lon,valid({$tz}),";
} else {
    echo "station,station_name,valid({$tz}),";
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
    echo $sid . $d[$delim] . $cities[$sid]["name"];
    if ($gis == "yes") {
        echo  $d[$delim] . $cities[$sid]["lat"] . $d[$delim] .  $cities[$sid]["lon"];
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
