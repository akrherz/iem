<?php
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$connection = iemdb("access");

$day = isset($_GET["day"]) ? $_GET["day"] : date("d");
$month = isset($_GET["month"]) ? $_GET["month"]: date("m");
$year = isset($_GET["year"]) ? $_GET["year"] : date("Y");
$network = isset($_GET["network"]) ? $_GET["network"] : "IA_ASOS";
$ts = mktime(0,0,0,$month, $day, $year);

$sql = sprintf("SELECT *, x(s.geom) as x, y(s.geom) as y from 
 summary_%s c, stations s WHERE s.network = '%s' and 
 day = '%s' and s.network = c.network and s.id = c.station
 ORDER by station ASC", date("Y", $ts), $network, date("Y-m-d", $ts) );
$rs = pg_exec($connection, $sql);

header("Content-type: text/plain");
echo "station,date,latitide,longitude,max_tmpf,min_tmpf,rain_inch,\n";

for( $i=0; $row = @pg_fetch_array($rs,$i); $i++)
{
  $maxt = ($row["max_tmpf"] > -90) ? $row["max_tmpf"] : "M";
  $mint = ($row["min_tmpf"] < 90) ? $row["min_tmpf"] : "M";
  $rain = ($row["pday"] >= 0) ? $row["pday"] : "M";
  echo sprintf("%s,%s,%s,%s,%s,%s,%s,\n", $row["station"], 
  date("Y-m-d", $ts), $row["y"], $row["x"], $maxt, $mint, $rain);  
}
?>
