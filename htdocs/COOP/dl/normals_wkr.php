<?php
 include("../../../config/settings.inc.php");
 /** normals_wkr.php
  *  - Download daily climate values
  */
include("$rootpath/include/database.inc.php");
include("$rootpath/include/network.php");     
$nt = new NetworkTable("IACLIMATE");
$cities = $nt->table;


$station = isset($_GET["station"]) ? strtolower(substr($_GET["station"],0,6)) 
                                   : die("No Station Specified");
$dloption = isset($_GET["dloption"]) ? $_GET["dloption"]
                                   : die("No download option specified");
$mode = isset($_GET["mode"]) ? $_GET["mode"] : 'station';
$source = isset($_GET["source"]) ? $_GET["source"] : 'climate71';
$month = isset($_GET["month"]) ? substr($_GET["month"],0,2) : 1;
$day = isset($_GET["day"]) ? substr($_GET["day"],0,2) : 1;
$datestr = "2000-$month-$day";

$con = iemdb('coop');

switch ($mode){
 case "station":
$rs = pg_prepare($con, "SELECT", "SELECT extract(month from valid) as month,
   extract(day from valid) as day, * from $source WHERE 
   station = $1 ORDER by valid ASC");
$rs = pg_execute($con, "SELECT", Array($station));
break;
 case "day":
$rs = pg_prepare($con, "SELECT", "SELECT extract(month from valid) as month,
   extract(day from valid) as day, * from $source WHERE 
   valid = $1 and station ~* 'ia' ORDER by station ASC");
$rs = pg_execute($con, "SELECT", Array($datestr));
 break;
}


$s = "Source,StationID,Name,Latitude,Longitude,Month,Day,Avg_High,Avg_Low,Avg_Precip,Max_Precip,Max_High,Min_High,Max_Low,Min_Low\n";
for($i=0; $row = @pg_fetch_array($rs,$i); $i++){
  $sid = $row["station"];
  $s .= sprintf("%s,%s,%s,%5.2f,%5.2f,%2d,%2d,%4.1f,%4.1f,%4.2f,%.2f,%.0f,%.0f,%.0f,%.0f\n", 
  	$source, $sid, $cities[strtoupper($sid)]["name"],
   $cities[strtoupper($sid)]["lat"], $cities[strtoupper($sid)]["lon"] ,
   $row["month"], $row["day"], $row["high"], $row["low"], $row["precip"], $row["max_precip"],
   $row["max_high"], $row["min_high"], $row["max_low"], $row["min_low"]);
}

switch($dloption){
 case "online":
   header("Content-type: text/plain");
 break;
 case "cdf":
   header("Content-type: application/octet-stream");
   header("Content-Disposition: attachment; filename=changeme.txt");
 break;

}

echo $s;

?>
