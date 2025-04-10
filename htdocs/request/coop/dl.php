<?php
/*
 * Download COOP observations from the QC'd table
 * DEPRECIATE this at some point...
 */
require_once "../../../config/settings.inc.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/mlib.php";
require_once "../../../include/network.php";
require_once "../../../include/forms.php";

$connection = iemdb("coop");
$network = isset($_REQUEST["network"]) ? substr($_REQUEST["network"], 0, 10) : "IACLIMATE";
$day1 = isset($_GET["day1"]) ? xssafe($_GET["day1"]) : die("No day1 specified");
$day2 = isset($_GET["day2"]) ? xssafe($_GET["day2"]) : die("No day2 specified");
$month1 = isset($_GET["month1"]) ? xssafe($_GET["month1"]) : die("No month1 specified");
$month2 = isset($_GET["month2"]) ? xssafe($_GET["month2"]) : die("No month2 specified");
$year1 = isset($_GET["year1"]) ? xssafe($_GET["year1"]) : die("No year1 specified");
$year2 = isset($_GET["year2"]) ? xssafe($_GET["year2"]) : die("No year2 specified");
$vars = isset($_GET["vars"]) ? $_GET["vars"] : die("No vars specified");

$gis = isset($_GET["gis"]) ? xssafe($_GET["gis"]) : 'no';
$delim = isset($_GET["delim"]) ? xssafe($_GET["delim"]) : ",";
$what = isset($_GET["what"]) ? xssafe($_GET["what"]) : 'dl';

$nt = new NetworkTable($network);
$cities = $nt->table;

$stations = isset($_GET["station"]) ? $_GET["station"] : die("No station specified");
if (!is_array($stations)) {
    $stations = array($stations);
}
$selectAll = false;
foreach ($stations as $key => $value) {
    if ($value == "_ALL") {
        $selectAll = true;
    }
    if (strlen($value) > 6 && !array_key_exists($value, $cities)) {
        xssafe("<tag>");
    }
}

if ($selectAll) {
    $stations = array_keys($cities);
}
$stationSQL = "{". implode(",", $stations) . "}";

if (isset($_GET["day"]))
    die("Incorrect CGI param, use day1, day2");

$ts1 = new DateTime("{$year1}-{$month1}-{$day1}");
$ts2 = new DateTime("{$year2}-{$month2}-{$day2}");


$num_vars = count($vars);
if ($num_vars == 0)  die("You did not specify data");

$sqlTS1 = $ts1->format("Y-m-d");
$sqlTS2 = $ts2->format("Y-m-d");
$table = "alldata";
$nicedate = $ts1->format("Y-m-d");

$d = array("space" => " ", "comma" => ",", "tab" => "\t");

$sqlStr = "SELECT station, *, to_char(day, 'YYYY/mm/dd') as dvalid, 
 extract(doy from day) as doy, 
 gddxx(50, 86, high, low) as gdd_50_86,
 gddxx(40, 86, high, low) as gdd_40_86,
 round((5.0/9.0 * (high - 32.0))::numeric,1) as highc,
 round((5.0/9.0 * (low - 32.0))::numeric,1) as lowc, 
 round((precip * 25.4)::numeric,1) as precipmm
 from $table WHERE day >= '" . $sqlTS1 . "' and day <= '" . $sqlTS2 . "' 
 and station = ANY($1) ORDER by day ASC";

/**
 * Must handle different ideas for what to do...
 **/

if ($what == "download") {
    header("Content-type: application/octet-stream");
    header("Content-Disposition: attachment; filename=changeme.txt");
} else {
    header("Content-type: text/plain");
}

if (in_array('daycent', $vars)) {
    /*
     * > Daily Weather Data File (use extra weather drivers = 0):
     * > 
     * > 1 1 1990 1 7.040 -10.300 0.000
     * > 
> NOTES:
> Column 1 - Day of month, 1-31
> Column 2 - Month of year, 1-12
> Column 3 - Year
> Column 4 - Day of the year, 1-366
> Column 5 - Maximum temperature for day, degrees C
> Column 6 - Minimum temperature for day, degrees C
> Column 7 - Precipitation for day, centimeters
     */
    if (sizeof($stations) > 1) die("Sorry, only one station request at a time for daycent option");
    if ($selectAll) die("Sorry, only one station request at a time for daycent option");
    $stname = iem_pg_prepare($connection, "SELECT extract(doy from day) as doy, high, low, precip,
        month, year, extract(day from day) as lday 
        from $table WHERE station = ANY($1) and day >= '" . $sqlTS1 . "' and day <= '" . $sqlTS2 . "' ORDER by day ASC");
    $rs = pg_execute($connection, $stname, array($stationSQL));
    echo "Daily Weather Data File (use extra weather drivers = 0):\n";
    echo "\n";
    while ($row = pg_fetch_assoc($rs)) {
        echo sprintf(
            "%s %s %s %s %.2f %.2f %.2f\n",
            $row["lday"],
            $row["month"],
            $row["year"],
            $row["doy"],
            f2c($row["high"]),
            f2c($row["low"]),
            $row["precip"] * 25.4
        );
    }
} else if (in_array('century', $vars)) {
    /*
     * Century format  (precip cm, avg high C, avg low C)
prec  1980   2.60   6.40   0.90   1.00   0.70   0.00   2.10   1.60   4.60   3.20   5.70   5.90
tmin  1980  14.66  12.10   7.33  -0.89  -5.45  -7.29 -11.65  -9.12  -7.03  -0.62   5.02  11.18
tmax  1980  33.24  30.50  27.00  18.37  11.35   9.90   0.39   3.93   6.77  14.92  19.77  28.85
prec  1981  12.00   7.20   0.60   4.90   1.10   0.30   0.70   0.30   4.50   5.10  11.50   4.10
tmin  1981  14.32  12.48   8.17   0.92  -3.25  -8.90  -9.47  -9.84  -4.10   2.90   4.84  10.87
tmax  1981  30.84  28.71  27.02  16.84  12.88   6.82   8.21   7.70  11.90  20.02  18.31  27.98
     */
    $response = "";
    if (sizeof($stations) > 1) {
        die("Sorry, only one station request at a time for century option");
    }
    if ($selectAll) {
        die("Sorry, only one station request at a time for century option");
    }
    $table = sprintf("alldata_%s", substr($stations[0], 0, 2));
    $stname = iem_pg_prepare($connection, "SELECT year, month, avg(high) as avgh, " .
        " avg(low) as avgl, sum(precip) as p" .
        " from $table WHERE station = ANY($3) and " .
        " year >= $1 and year <= $2 GROUP by year, month");
    $rs = pg_execute($connection, $stname, array($year1, $year2, $stationSQL));
    $monthly = array();
    while ($row = pg_fetch_assoc($rs)) {
        $key = sprintf("%s%02d", $row["year"], $row["month"]);
        $monthly[$key] = array(
            "tmax" => f2c($row["avgh"]),
            "tmin" => f2c($row["avgl"]),
            "prec" => $row["p"] * 2.54, // cm
        );
    }
    $idxs = array("prec", "tmin", "tmax");
    for ($y = $year1; $y <= $year2; $y++) {
        foreach ($idxs as $key => $val) {
            $response .= sprintf(
                "%s  %s%7.2f%7.2f%7.2f%7.2f%7.2f%7.2f%7.2f" .
                    "%7.2f%7.2f%7.2f%7.2f%7.2f\n",
                $val,
                $y,
                $monthly["{$y}01"][$val],
                $monthly["{$y}02"][$val],
                $monthly["{$y}03"][$val],
                $monthly["{$y}04"][$val],
                $monthly["{$y}05"][$val],
                $monthly["{$y}06"][$val],
                $monthly["{$y}07"][$val],
                $monthly["{$y}08"][$val],
                $monthly["{$y}09"][$val],
                $monthly["{$y}10"][$val],
                $monthly["{$y}11"][$val],
                $monthly["{$y}12"][$val]
            );
        }
    }
    /* Write back to the luser */
    header("Content-type: application/octet-stream");
    header(sprintf(
        "Content-Disposition: attachment; filename=%s.wth",
        $stations[0]
    ));
    die($response);
} else if (in_array('apsim', $vars)) {
    /*
     * [weather.met.weather]
latitude = 42.1 (DECIMAL DEGREES)
tav = 9.325084 (oC) ! annual average ambient temperature
amp = 29.57153 (oC) ! annual amplitude in mean monthly temperature
year          day           radn          maxt          mint          rain
()            ()            (MJ/m^2)      (oC)          (oC)          (mm)
 1986          1             7.38585       0.8938889    -7.295556      0
     */
    $network = sprintf("%sCLIMATE", substr($stations[0], 0, 2));
    $nt = new NetworkTable($network);
    $cities = $nt->table;
    $response = "[weather.met.weather]\n";
    $response .= sprintf(
        "latitude = %.1f (DECIMAL DEGREES)\n",
        $cities[$stations[0]]["lat"]
    );

    $sql = "SELECT avg((high+low)/2) from climate51 " .
        " WHERE station = ANY($1) ";
    $stname = iem_pg_prepare($connection, $sql);
    $rs = pg_execute($connection, $stname, array($stationSQL));
    $row = pg_fetch_assoc($rs, 0);
    $response .= sprintf(
        "tav = %.3f (oC) ! annual average ambient temperature\n",
        f2c($row['avg'])
    );
    $stname = iem_pg_prepare($connection, "select max(avg) as h, min(avg) as l from
            (SELECT extract(month from valid) as month, avg((high+low)/2.)
             from climate51 
             WHERE station = ANY($1) GROUP by month) as foo ");
    $rs = pg_execute($connection, $stname, array($stationSQL));
    $row = pg_fetch_assoc($rs, 0);
    $response .= sprintf(
        "amp = %.3f (oC) ! annual amplitude in mean monthly temperature\n",
        f2c($row['h']) - f2c($row['l'])
    );

    $response .= "year          day           radn          maxt          mint          rain
()            ()            (MJ/m^2)      (oC)          (oC)          (mm)\n";

    $stname = iem_pg_prepare($connection, "SELECT extract(doy from day) as doy, high," .
        " low, precip, month, year, extract(day from day) as lday, station, year," .
        " coalesce(narr_srad, merra_srad, hrrr_srad) as srad" .
        " from $table " .
        " WHERE station = ANY($1) and " .
        " day >= '" . $sqlTS1 . "' and day <= '" . $sqlTS2 . "' ORDER by day ASC");
    $rs = pg_execute($connection, $stname, array($stationSQL));
    while ($row = pg_fetch_assoc($rs)) {
        $response .= sprintf(
            " %s         %s        %.4f         %.4f      %.4f     %.2f\n",
            $row["year"],
            $row["doy"],
            ($row["srad"] === null) ? -99 : $row["srad"],
            f2c($row["high"]),
            f2c($row["low"]),
            $row["precip"] * 25.4
        );
    }

    /* Write back to the luser */
    header("Content-type: application/octet-stream");
    header("Content-Disposition: attachment; filename=fancypants.met");
    die($response);
} else if (in_array('dndc', $vars)) {
    /*
     * One file per year! named StationName / StationName_YYYY.txt
     * julian day, tmax C , tmin C, precip cm seperated by space
     */
    $stname = iem_pg_prepare($connection, "SELECT extract(doy from day) as doy, high," .
        " low, precip, month, year, extract(day from day) as lday, station, year " .
        " from $table " .
        " WHERE station = ANY($1) and " .
        " day >= '" . $sqlTS1 . "' and day <= '" . $sqlTS2 . "' ORDER by day ASC");
    $rs = pg_execute($connection, $stname, array($stationSQL));
    $zipfiles = array();
    while ($row = pg_fetch_assoc($rs)) {
        $sname = str_replace(" ", "_", $cities[$row["station"]]["name"]);
        $fn = sprintf("%s/%s_%s.txt", $sname, $sname, $row["year"]);
        if (!array_key_exists($fn, $zipfiles)) {
            $zipfiles[$fn] = "";
        }
        $zipfiles[$fn] .= sprintf(
            "%s %s %s %s\n",
            $row["doy"],
            f2c($row["high"]),
            f2c($row["low"]),
            $row["precip"] * 2.54
        );
    }
    chdir("/tmp");
    $zip = new ZipArchive;
    $res = $zip->open('dndc.zip', ZipArchive::CREATE);
    foreach ($zipfiles as $key => $val) {
        $zip->addFromString($key, $val);
    }
    $zip->close();
    /* Write back to the luser */
    header("Content-type: application/octet-stream");
    header("Content-Disposition: attachment; filename=dndc.zip");
    readfile("dndc.zip");
} else if (in_array('salus', $vars)) {
    /*
     * > Daily Weather Data File (use extra weather drivers = 0):

StationID, Year, DOY, SRAD, Tmax, Tmin, Rain, DewP, Wind, Par, dbnum
CTRL, 1981, 1, 5.62203, 2.79032, -3.53361, 5.43766, NaN, NaN, NaN, 2
CTRL, 1981, 2, 3.1898, 1.59032, -6.83361, 1.38607, NaN, NaN, NaN, 3
    */
    if (sizeof($stations) > 1) die("Sorry, only one station request at a time for daycent option");
    if ($selectAll) die("Sorry, only one station request at a time for daycent option");
    $stname = iem_pg_prepare($connection, "SELECT extract(doy from day) as doy, high," .
        " low, precip, month, year, extract(day from day) as lday, station, year," .
        " coalesce(narr_srad, merra_srad, hrrr_srad) as srad" .
        " from $table WHERE station = ANY($1) and " .
        " day >= '" . $sqlTS1 . "' and day <= '" . $sqlTS2 . "' ORDER by day ASC");
    $rs = pg_execute($connection, $stname, array($stationSQL));
    echo "StationID, Year, DOY, SRAD, Tmax, Tmin, Rain, DewP, Wind, Par, dbnum\n";
    for ($i = 0; $row = pg_fetch_assoc($rs); $i++) {
        echo sprintf(
            "%s, %s, %s, %.4f, %.2f, %.2f, %.2f, , , , %s\n",
            substr($row["station"], 0, 4),
            $row["year"],
            $row["doy"],
            ($row["srad"] === null) ? -99 : $row["srad"],
            f2c($row["high"]),
            f2c($row["low"]),
            $row["precip"] * 25.4,
            $i + 2
        );
    }
} else if ($what != "plot") {

    $stname = iem_pg_prepare($connection, $sqlStr);
    $rs =  pg_execute($connection, $stname, Array($stationSQL));

    if ($gis == "yes") {
        echo "station" . $d[$delim] . "station_name" . $d[$delim] . "lat" . $d[$delim] . "lon" . $d[$delim] . "day" . $d[$delim] . "julianday" . $d[$delim];
    } else {
        echo "station" . $d[$delim] . "station_name" . $d[$delim] . "day" . $d[$delim] . "julianday" . $d[$delim];
    }
    for ($j = 0; $j < $num_vars; $j++) {
        echo $vars[$j] . $d[$delim];
    }
    echo "\r\n";

    while ($row = pg_fetch_assoc($rs)) {
        $sid = $row["station"];
        echo $sid . $d[$delim] . $cities[$sid]["name"];
        if ($gis == "yes") {
            echo  $d[$delim] . $cities[$sid]["lat"] . $d[$delim] .  $cities[$sid]["lon"];
        }
        echo $d[$delim] . $row["dvalid"] . $d[$delim] . $row["doy"] . $d[$delim];
        for ($j = 0; $j < $num_vars; $j++) {
            echo $row[$vars[$j]] . $d[$delim];
        }
        echo "\r\n";
    }
}
