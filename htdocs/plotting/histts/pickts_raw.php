<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$connection = iemdb("asos");
$connection2 = iemdb("rwis");

$station = isset($_GET["station"]) ? $_GET["station"]: "";
$network = isset($_GET["network"]) ? $_GET["network"]: "IA_ASOS";
$year = isset($_GET["year"]) ? $_GET["year"]: date("Y");
$month = isset($_GET["month"]) ? $_GET["month"]: date("m");
$day = isset($_GET["day"]) ? $_GET["day"]: date("d");
$shour = isset($_GET["shour"]) ? $_GET["shour"]: 0;
$duration = isset($_GET["duration"])? $_GET["duration"]: 12;


$stime = $year ."-". $month ."-". $day ." ". $shour .":00:00";

$query1 = "SET TIME ZONE 'GMT'";
$query2 = "SELECT tmpf, dwpf, sknt, drct, to_char(valid, 'yymmdd/HH24MI') as valid from t". $year ." WHERE station = '". $station ."' 
	and valid BETWEEN '". $stime ."' and  ('". $stime ."'::timestamp + '". $duration ." hours'::interval ) ORDER by valid ASC ";

if ( strlen($station) == 3 ) {	
	$result = pg_exec($connection, $query1);
	$result = pg_exec($connection, $query2);
} else {
        $result = pg_exec($connection2, $query1);
        $result = pg_exec($connection2, $query2);
}

$ydata = array();
$ydata2 = array();
$xlabel= array();

echo "<PRE>\n";
echo "Station\tValid          \tTMP (F)\tDWP (F)\tSPED (kt)\tDRCT (deg)\n";
for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{ 
  echo $station ."\t". $row["valid"] ."\t". $row["tmpf"] ."\t". $row["dwpf"] ."\t". $row["sknt"] ."\t". $row["drct"] ."\n";
}

echo "</PRE>\n";

pg_close($connection);
pg_close($connection2);

?>
