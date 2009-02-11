<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
 $connection = iemdb("hads");
include("$rootpath/include/network.php");
$nt = new NetworkTable("DCP");
$cities = $nt->table;


$delim = isset($_GET["delim"]) ? $_GET["delim"]: ",";
$sample = isset($_GET["sample"]) ? $_GET["sample"]: "1min";
$what = isset($_GET["what"]) ? $_GET["what"]: 'dl';

$day1 = isset($_GET["day1"]) ? $_GET["day1"] : die("No day1 specified");
$day2 = isset($_GET["day2"]) ? $_GET["day2"] : die("No day2 specified");
$month1 = isset($_GET["month1"]) ? $_GET["month1"]: die("No month1 specified");
$month2 = isset($_GET["month2"]) ? $_GET["month2"]: die("No month2 specified");
$year = isset($_GET["year"]) ? $_GET["year"] : die("No year specified");
$hour1 = isset($_GET["hour1"]) ? $_GET["hour1"]: die("No hour1 specified");
$hour2 = isset($_GET["hour2"]) ? $_GET["hour2"]: die("No hour2 specified");
$minute1 = isset($_GET["minute1"]) ? $_GET["minute1"]: die("No minute1 specified");
$minute2 = isset($_GET["minute2"]) ? $_GET["minute2"]: die("No minute2 specified");


$station = $_GET["station"];
$stations = $_GET["station"];
$stationString = "(";
$selectAll = false;
foreach ($stations as $key => $value){
  if ($value == "_ALL"){
    $selectAll = true;
  } 
  $stationString .= " '". $value ."',";
}


if ($selectAll){
  $stationString = "(";
  foreach ($Rcities as $key => $value){
    $stationString .= " '". $key ."',";
  }
}

$stationString = substr($stationString, 0, -1);
$stationString .= ")";

if (isset($_GET["day"]))
  die("Incorrect CGI param, use day1, day2");

$ts1 = mktime($hour1, $minute1, 0, $month1, $day1, $year) or 
  die("Invalid Date Format");
$ts2 = mktime($hour2, $minute2, 0, $month2, $day2, $year) or
  die("Invalid Date Format");

if ($selectAll && $day1 != $day2)
	$ts2 = $ts1 + 86400;


$sqlStr = "SELECT *, ";

$sqlTS1 = strftime("%Y-%m-%d %H:%M", $ts1);
$sqlTS2 = strftime("%Y-%m-%d %H:%M", $ts2);
$table = strftime("raw%Y", $ts1);
$nicedate = strftime("%Y-%m-%d", $ts1);

$d = Array("space" => " ", "comma" => "," , "tab" => "\t");

$sqlStr .= "to_char(valid, 'YYYY-MM-DD HH24:MI') as dvalid from ".$table ;
$sqlStr .= " WHERE valid >= '".$sqlTS1."' and valid <= '".$sqlTS2 ."' ";
$sqlStr .= " and station IN ". $stationString ." ORDER by valid ASC";

/**
 * Must handle different ideas for what to do...
 **/

if ($what == "download"){
 header("Content-type: application/octet-stream");
 header("Content-Disposition: attachment; filename=changeme.txt");
} else {
 header("Content-type: text/plain");
}


 $query1 = "SET TIME ZONE 'GMT'";

 $result = pg_exec($connection, $query1);
 $rs =  pg_exec($connection, $sqlStr);

 pg_close($connection);
echo "station".$d[$delim] ."station_name". $d[$delim] ."valid(GMT)". $d[$delim] ."variable". $d[$delim] ."value\n";

 for( $i=0; $row = @pg_fetch_array($rs,$i); $i++) 
 {
  $sid = $row["station"];
  echo $sid . $d[$delim] . $cities[$sid]["name"] ;
  echo $d[$delim] . $row["dvalid"] . $d[$delim];
  echo $row["key"]. $d[$delim] . $row["value"] ;
  echo "\n";
 }

?>
