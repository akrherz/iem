<?php
/**
 * dl.php  26 Jun 2004 
 */

include("/mesonet/www/html/include/COOPstations.php");
include("adodb-time.inc.php");

$station = $_GET["station"];
$stations = $_GET["station"];
$stationString = "(";
$selectAll = false;
$multipleSelected = false;
$i = 0;
foreach ($stations as $key => $value){
  if ($value == "_ALL"){
    $selectAll = true;
  }
  $stationString .= " '". $value ."',";
  $i++;
}
if ($i > 1) $multipleSelected = true;


if ($selectAll){
  $stationString = "(";
  foreach ($cities as $key => $value){
    $stationString .= " '". $key ."',";
  }
}

$stationString = substr($stationString, 0, -1);
$stationString .= ")";

if ((strlen($day) > 0))
  die("Incorrect CGI param, use day1, day2");

$ts1 = adodb_mktime(0, 0, 0, $month1, $day1, $year1) or 
  die("Invalid Date Format");
$ts2 = adodb_mktime(0, 0, 0, $month2, $day2, $year2) or
  die("Invalid Date Format");

if ($multipleSelected)
	$ts2 = adodb_mktime(0, 0, 0, $month2, $day2, $year1);

$num_vars = count($vars);
if ( $num_vars == 0 )  die("You did not specify data");

$sqlStr = "SELECT stationid, ";
for ($i=0; $i< $num_vars;$i++){
  $sqlStr .= $vars[$i] ." as var".$i.", ";
}

$sqlTS1 = adodb_date("Y-m-d", $ts1);
$sqlTS2 = adodb_date("Y-m-d", $ts2);
$table = "alldata";
$nicedate = adodb_date("Y-m-d", $ts1);

$d = Array("space" => " ", "comma" => "," , "tab" => "\t");

$sqlStr .= "day as dvalid from ".$table ;
$sqlStr .= " WHERE day >= '".$sqlTS1."' and day <= '".$sqlTS2 ."' ";
$sqlStr .= " and stationid IN ". $stationString ." ORDER by day ASC";

/**
 * Must handle different ideas for what to do...
 **/

if ($what == "download"){
 header("Content-type: application/octet-stream");
 header("Content-Disposition: attachment; filename=changeme.txt");
} else {
 header("Content-type: text/plain");
}

if ($what != "plot"){
 $connection = pg_connect("10.10.10.20","5432","coop");

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
  echo "\n";

 for( $i=0; $row = @pg_fetch_array($rs,$i); $i++) 
 {
  $sid = $row["stationid"];
  echo $sid . $d[$delim] . $cities[$sid]["city"] ;
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
  echo "\n";
 }
}

?>
