<?php
require_once "../../../config/settings.inc.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/forms.php";

$year1 = get_int404("year1", 2010);
$year2 = get_int404("year2", 2010);
$hour1 = get_int404("hour1", 0);
$hour2 = get_int404("hour2", 0);
$day1 = get_int404("day1", 1);
$day2 = get_int404("day2", 1);
$month1 = get_int404("month1", 1);
$month2 = get_int404("month2", 2);
$vars = array_key_exists("vars", $_GET) ? $_GET["vars"] : ["tmpf"];
$sample = get_str404("sample", "1min");
$dl_option = get_str404("dl_option", "display");
$delim = get_str404("delim", ",");

$ts1 = mktime($hour1, 0, 0, $month1, $day1, $year1);
$ts2 = mktime($hour2, 0, 0, $month2, $day2, $year2);

$num_vars = count($vars);

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

$stations = array_key_exists("station", $_GET) ? $_GET["station"] : ["SAMI4"];
$stationSQL = "{". implode(",", $stations) . "}";

$sqlStr .= "to_char(valid, 'YYYY-MM-DD HH24:MI') as dvalid from alldata";
$sqlStr .= " WHERE valid >= '" . $sqlTS1 . "' and valid <= '" . $sqlTS2 . "' ";
$sqlStr .= " and station = ANY($1) and ";
$sqlStr .= " extract(minute from valid)::int % " . $sampleStr[$sample] . " = 0 ";
$sqlStr .= " ORDER by valid ASC";

$stname = iem_pg_prepare($connection, $sqlStr);
$rs = pg_execute($connection, $stname, array($stationSQL));

if (pg_num_rows($rs) == 0) {
    http_response_code(422);
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

    while ($row = pg_fetch_assoc($rs)) {
        printf("%s%s%s", $row["station"], $d[$delim],  $row["dvalid"]);
        for ($j = 0; $j < $num_vars; $j++) {
            printf("%s%6s", $d[$delim], $row["var" . $j]);
        }
        echo "\n";
    }
} else {

    while ($row = pg_fetch_assoc($rs)) {
        printf("%s%s%s", $row["station"], $d[$delim], $row["dvalid"]);
        for ($j = 0; $j < $num_vars; $j++) {
            printf("%s%6s", $d[$delim], $row["var" . $j]);
        }
        echo "\n";
    }
}
