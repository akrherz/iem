<?php
include("../../../config/settings.inc.php");
$network = isset($_GET['network']) ? $_GET["network"] : 'IA_COOP';
include("$rootpath/include/database.inc.php");
 $connection = iemdb("iem");
include("$rootpath/include/network.php");
$nt = new NetworkTable($network);
$cities = $nt->table;

$delim = isset($_GET["delim"]) ? $_GET["delim"]: ",";
$what = isset($_GET["what"]) ? $_GET["what"]: 'dl';

$day1 = isset($_GET["day1"]) ? $_GET["day1"] : die("No day1 specified");
$day2 = isset($_GET["day2"]) ? $_GET["day2"] : die("No day2 specified");
$month1 = isset($_GET["month1"]) ? $_GET["month1"]: die("No month1 specified");
$month2 = isset($_GET["month2"]) ? $_GET["month2"]: die("No month2 specified");
$year1 = isset($_GET["year1"]) ? $_GET["year1"] : die("No year1 specified");
$year2 = isset($_GET["year2"]) ? $_GET["year2"] : die("No year2 specified");
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

$ts1 = mktime($hour1, $minute1, 0, $month1, $day1, $year1) or 
  die("Invalid Date Format");
$ts2 = mktime($hour2, $minute2, 0, $month2, $day2, $year2) or
  die("Invalid Date Format");

$sqlTS1 = strftime("%Y-%m-%d", $ts1);
$sqlTS2 = strftime("%Y-%m-%d", $ts2);
$nicedate = strftime("%Y-%m-%d", $ts1);

$d = Array("space" => " ", "comma" => "," , "tab" => "\t");

$sqlStr = "SELECT s.*,t.id, day from summary s JOIN stations t on (t.iemid = s.iemid)";
$sqlStr .= " WHERE day >= '".$sqlTS1."' and day <= '".$sqlTS2 ."' ";
$sqlStr .= " and id IN ". $stationString ." ORDER by s.day ASC";

if ($what == "download"){
 header("Content-type: application/octet-stream");
 header("Content-Disposition: attachment; filename=changeme.txt");
} else {
 header("Content-type: text/plain");
}

$rs = pg_prepare($connection, "SELECT", $sqlStr);
$rs = pg_execute($connection, "SELECT", Array() );
pg_close($connection);

function cleaner($v){
	if ($v == 0.0001) return "T";
	if ($v == -99) return 'M';
	return $v;
}

 /* Load data into an array, yucky... */
 $data = "nwsli,date,high_F,low_F,precip_inch,snow_inch,snowd_inch\n";
 for( $i=0; $row = @pg_fetch_array($rs,$i); $i++) 
 {
   $data .= sprintf("%s%s%s%s%s%s%s%s%s%s%s%s%s\n", $row["id"],$d[$delim], $row["day"],
   		$d[$delim], cleaner($row["max_tmpf"]), $d[$delim], 
   		cleaner($row["min_tmpf"]), $d[$delim],
   		cleaner($row["pday"]), $d[$delim], cleaner($row["snow"]),$d[$delim],
   		cleaner($row["snowd"]));
 }

 echo $data;
?>
