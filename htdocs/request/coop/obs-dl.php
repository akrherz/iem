<?php
require_once "../../../config/settings.inc.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/network.php";
$network = isset($_GET['network']) ? substr($_GET["network"], 0, 30) : 'IA_COOP';
$connection = iemdb("iem");
$nt = new NetworkTable($network);
$cities = $nt->table;

$delim = isset($_GET["delim"]) ? $_GET["delim"] : "comma";
$what = isset($_GET["what"]) ? $_GET["what"] : 'dl';

$day1 = isset($_GET["day1"]) ? $_GET["day1"] : die("No day1 specified");
$day2 = isset($_GET["day2"]) ? $_GET["day2"] : die("No day2 specified");
$month1 = isset($_GET["month1"]) ? $_GET["month1"] : die("No month1 specified");
$month2 = isset($_GET["month2"]) ? $_GET["month2"] : die("No month2 specified");
$year1 = isset($_GET["year1"]) ? $_GET["year1"] : die("No year1 specified");
$year2 = isset($_GET["year2"]) ? $_GET["year2"] : die("No year2 specified");
$hour1 = 0;
$hour2 = 0;
$minute1 = 0;
$minute2 = 0;


$station = $_GET["station"];
$stations = $_GET["station"];
$stationString = "(";
$selectAll = false;
foreach ($stations as $key => $value) {
    if ($value == "_ALL") {
        $selectAll = true;
    }
    $stationString .= " '" . $value . "',";
}


if ($selectAll) {
    $stationString = "(";
    foreach ($Rcities as $key => $value) {
        $stationString .= " '" . $key . "',";
    }
}

$stationString = substr($stationString, 0, -1);
$stationString .= ")";

$ts1 = mktime($hour1, $minute1, 0, $month1, $day1, $year1) or
    die("Invalid Date Format");
$ts2 = mktime($hour2, $minute2, 0, $month2, $day2, $year2) or
    die("Invalid Date Format");

$sqlTS1 = date("Y-m-d", $ts1);
$sqlTS2 = date("Y-m-d", $ts2);
$nicedate = date("Y-m-d", $ts1);

$d = array("space" => " ", "comma" => ",", "tab" => "\t");

$sqlStr = <<<EOF
 SELECT s.*,t.id, day, 
 to_char(coop_valid at time zone t.tzname, 'HH PM') as cv
 from summary s JOIN stations t on (t.iemid = s.iemid)
 WHERE day >= '{$sqlTS1}' and day <= '{$sqlTS2}' 
 and id IN {$stationString} and network = '{$network}' ORDER by s.day ASC
EOF;

if ($what == "download") {
    header("Content-type: application/octet-stream");
    header("Content-Disposition: attachment; filename=changeme.txt");
} else {
    header("Content-type: text/plain");
}

$rs = pg_prepare($connection, "SELECT", $sqlStr);
$rs = pg_execute($connection, "SELECT", array());
pg_close($connection);

function cleaner($v)
{
    if ($v == 0.0001) return "T";
    if ($v == -99) return 'M';
    return $v;
}

$cols = array(
    "nwsli", "date", "time", "high_F", "low_F", "precip",
    "snow_inch", "snowd_inch"
);
$data = implode($d[$delim], $cols) . "\n";
for ($i = 0; $row = pg_fetch_array($rs); $i++) {
    $data .= sprintf(
        "%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s\n",
        $row["id"],
        $d[$delim],
        $row["day"],
        $d[$delim],
        $row["cv"],
        $d[$delim],
        cleaner($row["max_tmpf"]),
        $d[$delim],
        cleaner($row["min_tmpf"]),
        $d[$delim],
        cleaner($row["pday"]),
        $d[$delim],
        cleaner($row["snow"]),
        $d[$delim],
        cleaner($row["snowd"])
    );
}

echo $data;
