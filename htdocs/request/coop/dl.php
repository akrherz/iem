<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$connection =iemdb("coop");
include("$rootpath/include/mlib.php");
$network = isset($_REQUEST["network"]) ? substr($_REQUEST["network"],0,10) : "IACLIMATE";
$day1 = isset($_GET["day1"]) ? $_GET["day1"] : die("No day1 specified");
$day2 = isset($_GET["day2"]) ? $_GET["day2"] : die("No day2 specified");
$month1 = isset($_GET["month1"]) ? $_GET["month1"]: die("No month1 specified");
$month2 = isset($_GET["month2"]) ? $_GET["month2"]: die("No month2 specified");
$year1 = isset($_GET["year1"]) ? $_GET["year1"] : die("No year1 specified");
$year2 = isset($_GET["year2"]) ? $_GET["year2"] : die("No year2 specified");
$vars = isset($_GET["vars"]) ? $_GET["vars"] : die("No vars specified");

$gis = isset($_GET["gis"]) ? $_GET["gis"]: 'no';
$delim = isset($_GET["delim"]) ? $_GET["delim"]: ",";
$sample = isset($_GET["sample"]) ? $_GET["sample"]: "1min";
$what = isset($_GET["what"]) ? $_GET["what"]: 'dl';


include("$rootpath/include/network.php");
$nt = new NetworkTable($network);
$cities = $nt->table;
include("adodb-time.inc.php");

$station = $_GET["station"];
$stations = $_GET["station"];
$stationString = "(";
$selectAll = 0;
$i = 0;
foreach ($stations as $key => $value){
  if ($value == "_ALL"){
    $selectAll = 1;
  }
  $stationString .= " '". $value ."',";
  $i++;
}


if ($selectAll){
  $stationString = "(";
  foreach ($cities as $key => $value){
    $stationString .= " '". $key ."',";
  }
}

$stationString = substr($stationString, 0, -1);
$stationString .= ")";

if (isset($_GET["day"]))
  die("Incorrect CGI param, use day1, day2");

$ts1 = adodb_mktime(0, 0, 0, $month1, $day1, $year1) or 
  die("Invalid Date Format");
$ts2 = adodb_mktime(0, 0, 0, $month2, $day2, $year2) or
  die("Invalid Date Format");


$num_vars = count($vars);
if ( $num_vars == 0 )  die("You did not specify data");

$sqlStr = "SELECT station, ";
for ($i=0; $i< $num_vars;$i++){
  $sqlStr .= $vars[$i] ." as var".$i.", ";
}

$sqlTS1 = adodb_date("Y-m-d", $ts1);
$sqlTS2 = adodb_date("Y-m-d", $ts2);
$table = "alldata";
$nicedate = adodb_date("Y-m-d", $ts1);

$d = Array("space" => " ", "comma" => "," , "tab" => "\t");

$sqlStr .= "to_char(day, 'YYYY/mm/dd') as dvalid from ".$table ;
$sqlStr .= " WHERE day >= '".$sqlTS1."' and day <= '".$sqlTS2 ."' ";
$sqlStr .= " and station IN ". $stationString ." ORDER by day ASC";

/**
 * Must handle different ideas for what to do...
 **/

if ($what == "download"){
 header("Content-type: application/octet-stream");
 header("Content-Disposition: attachment; filename=changeme.txt");
} else {
 header("Content-type: text/plain");
}

if (in_array('daycent', $vars)){
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
	pg_prepare($connection, "DAYCENT", "SELECT extract(doy from day) as doy, high, low, precip,
		month, year, extract(day from day) as lday 
		from $table WHERE station IN ". $stationString ." and day >= '".$sqlTS1."' and day <= '".$sqlTS2 ."' ORDER by day ASC");
	$rs = pg_execute($connection, 'DAYCENT', Array());
	echo "Daily Weather Data File (use extra weather drivers = 0):\n";
	echo "\n";
	for ($i=0;$row=@pg_fetch_assoc($rs,$i);$i++){
		echo sprintf("%s %s %s %s %.2f %.2f %.2f\n", $row["lday"], $row["month"], $row["year"], 
		$row["doy"], f2c($row["high"]), f2c($row["low"]), $row["precip"] * 25.4);
	}
	
}
else if ($what != "plot"){
 
 $rs =  pg_exec($connection, $sqlStr);

 pg_close($connection);
  if ($gis == "yes"){
    echo "station". $d[$delim] ."station_name". $d[$delim] ."lat". $d[$delim] ."lon". $d[$delim] ."day". $d[$delim];
  } else {
    echo "station". $d[$delim] ."station_name". $d[$delim] ."day". $d[$delim] ;
  }
  for ($j=0; $j < $num_vars;$j++){
    echo $vars[$j]. $d[$delim];
    if ($vars[$j] == "ca1") echo "ca1code". $d[$delim];
    if ($vars[$j] == "ca2") echo "ca2code". $d[$delim];
    if ($vars[$j] == "ca3") echo "ca3code". $d[$delim];
  }
  echo "\r\n";

 for( $i=0; $row = @pg_fetch_array($rs,$i); $i++) 
 {
  $sid = $row["station"];
  echo $sid . $d[$delim] . $cities[$sid]["name"] ;
  if ($gis == "yes"){
     echo  $d[$delim] . $cities[$sid]["lat"] . $d[$delim] .  $cities[$sid]["lon"] ;
  } 
  echo $d[$delim] . $row["dvalid"] . $d[$delim];
  for ($j=0; $j < $num_vars;$j++){
    echo $row["var".$j]. $d[$delim];
    if ($vars[$j] == "ca1") echo $skycover[$row["var".$j]] . $d[$delim];
    if ($vars[$j] == "ca2") echo $skycover[$row["var".$j]] . $d[$delim];
    if ($vars[$j] == "ca3") echo $skycover[$row["var".$j]] . $d[$delim];
  }
  echo "\r\n";
 }
}

?>
