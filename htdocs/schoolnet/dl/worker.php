<?php
require_once "../../../config/settings.inc.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/forms.php";

$year1 = isset($_GET["year1"]) ? xssafe($_GET["year1"]) : die("No year1");
$year2 = isset($_GET["year2"]) ? xssafe($_GET["year2"]) : die("No year2");
$hour1 = isset($_GET["hour1"]) ? xssafe($_GET["hour1"]) : die("No hour1");
$hour2 = isset($_GET["hour2"]) ? xssafe($_GET["hour2"]) : die("No hour2");
$day1 = isset($_GET["day1"]) ? xssafe($_GET["day1"]) : die("No day1");
$day2 = isset($_GET["day2"]) ? xssafe($_GET["day2"]) : die("No day2");
$month1 = isset($_GET["month1"]) ? xssafe($_GET["month1"]) : die("No month1");
$month2 = isset($_GET["month2"]) ? xssafe($_GET["month2"]) : die("No month2");
$vars = isset($_GET["vars"]) ? $_GET["vars"] : die("No vars");
$sample = isset($_GET["sample"]) ? xssafe($_GET["sample"]) : die("No Sample");
$dl_option = isset($_GET["dl_option"]) ? xssafe($_GET["dl_option"]) : die("No dl_option");
$delim = isset($_GET["delim"]) ? xssafe($_GET["delim"]) : die("No delim");

$ts1 = mktime($hour1, 0, 0, $month1, $day1, $year1) or
    die("Invalid Date Format");
$ts2 = mktime($hour2, 0, 0, $month2, $day2, $year2) or
    die("Invalid Date Format");

if ($ts1 >= $ts2) {
    die("Error:  Your 'End Date' is before your 'Start Date'!");
}

$num_vars = count($vars);
if ($num_vars == 0)  die("You did not specify data");

$connection = iemdb("snet");

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

$d = array(
    "comma" => ",",
    "space" => " ",
    "tab" => "\t"
);

$stations = $_GET["station"];
$stationSQL = "{". implode(",", $stations) . "}";

$sqlStr .= "to_char(valid, 'YYYY-MM-DD HH24:MI') as dvalid from alldata";
$sqlStr .= " WHERE valid >= '" . $sqlTS1 . "' and valid <= '" . $sqlTS2 . "' ";
$sqlStr .= " and station = ANY($1) and ";
$sqlStr .= " extract(minute from valid)::int % " . $sampleStr[$sample] . " = 0 ";
$sqlStr .= " ORDER by valid ASC";

$stname = uniqid();
pg_prepare($connection, $stname, $sqlStr);
$rs = pg_execute($connection, $stname, array($stationSQL));

if (pg_num_rows($rs) == 0) {
    die("Did not find any data for this query!");
} else if ($dl_option == "download") {
    header("Content-type: application/octet-stream");
    header("Content-Disposition: attachment; filename=snetData.dat");
} else {
    header("Content-type: text/plain");
}

printf("%s%s%s", "STID", $d[$delim], "DATETIME");
for ($j = 0; $j < $num_vars; $j++) {
    printf("%s%6s", $d[$delim], $vars[$j]);
}
echo "\n";
if ($dl_option == "download") {

    for ($i = 0; $row = pg_fetch_assoc($rs); $i++) {
        printf("%s%s%s", $row["station"], $d[$delim],  $row["dvalid"]);
        for ($j = 0; $j < $num_vars; $j++) {
            printf("%s%6s", $d[$delim], $row["var" . $j]);
        }
        echo "\n";
    }
} else {

    for ($i = 0; $row = pg_fetch_assoc($rs); $i++) {
        printf("%s%s%s", $row["station"], $d[$delim], $row["dvalid"]);
        for ($j = 0; $j < $num_vars; $j++) {
            printf("%s%6s", $d[$delim], $row["var" . $j]);
        }
        echo "\n";
    }
}
