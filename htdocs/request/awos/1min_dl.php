<?php
/**
 * Script that does the processing or hands off to plotter.
 * Must send content-type early, if we want this to work
 * 11 Nov 2002:	Add Delimitation argument
 *  4 Jun 2003	Support for multiple stations
 * 24 Mar 2004	Support AWOS sky coverage codes
 */

include("/mesonet/www/html/include/awosLoc.php");

$skycover = Array(
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
 255 => "MISSING");

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
  foreach ($Wcities as $key => $value){
    $stationString .= " '". $key ."',";
  }
}

$stationString = substr($stationString, 0, -1);
$stationString .= ")";

if ((strlen($day) > 0))
  die("Incorrect CGI param, use day1, day2");

$ts1 = mktime($hour1, $minute1, 0, $month, $day1, $year) or 
  die("Invalid Date Format");
$ts2 = mktime($hour2, $minute2, 0, $month, $day2, $year) or
  die("Invalid Date Format");

if ($selectAll && $day1 != $day2)
	$ts2 = $ts1 + 86400;

$num_vars = count($vars);
if ( $num_vars == 0 )  die("You did not specify data");

$sqlStr = "SELECT station, ";
for ($i=0; $i< $num_vars;$i++){
  $sqlStr .= $vars[$i] ." as var".$i.", ";
}

$sqlTS1 = strftime("%Y-%m-%d %H:%M", $ts1);
$sqlTS2 = strftime("%Y-%m-%d %H:%M", $ts2);
$table = strftime("t%Y_%m", $ts1);
$nicedate = strftime("%Y-%m-%d", $ts1);

$sampleStr = Array("1min" => "1",
  "5min" => "5",
  "10min" => "10",
  "20min" => "20",
  "1hour" => "60");

$d = Array("space" => " ", "comma" => "," , "tab" => "\t");

$sqlStr .= "to_char(valid, 'YYYY-MM-DD HH24:MI') as dvalid from ".$table ;
$sqlStr .= " WHERE valid >= '".$sqlTS1."' and valid <= '".$sqlTS2 ."' ";
$sqlStr .= " and extract(minute from valid)::int % ".$sampleStr[$sample] ." = 0 ";
$sqlStr .= " and station IN ". $stationString ." ORDER by valid ASC";


/**
 * Must handle different ideas for what to do...
 **/

if ($what == "download"){
 header("Content-type: application/octet-stream");
 header("Content-Disposition: attachment; filename=changeme.txt");
} else if ($what == "plot"){
 include ("../../plotting/jpgraph/jpgraph.php");
include ("../../plotting/jpgraph/jpgraph_line.php");
 if ($selectAll){
  foreach ($Wcities as $key => $value){
   $station = $key;
   include ("plot_1min.php");
  }
 } else {
   foreach ($stations as $key => $value){
     $station = $value;

     include ("plot_1min.php");
   }
 }
} else {
 header("Content-type: text/plain");
}

if ($what != "plot"){
 $connection = pg_connect("10.10.10.20","5432","awos");

 $query1 = "SET TIME ZONE 'GMT'";

 $result = pg_exec($connection, $query1);
 $rs =  pg_exec($connection, $sqlStr);

 pg_close($connection);
  if ($gis == "yes"){
    echo "station,station_name,lat,lon,valid(GMT),";
  } else {
    echo "station,station_name,valid(GMT),";
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
  $sid = $row["station"];
  echo $sid . $d[$delim] . $Wcities[$sid]["city"] ;
  if ($gis == "yes"){
     echo  $d[$delim] . $Wcities[$sid]["lat"] . $d[$delim] .  $Wcities[$sid]["lon"] ;
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
