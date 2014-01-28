<?php 
/*
 * Generate GR placefile of IDOT Truck Temperatures
 */
header("Content-type: text/plain");

echo 'Title: IDOT Trucks
Refresh: 5
Color: 200 200 255
Font: 1, 11, 1, "Courier New"

';
include("../../../config/settings.inc.php");
include("../../../include/database.inc.php");
$dbconn = iemdb("postgis");

$rs = pg_query($dbconn, "SELECT airtemp, valid, ST_x(geom) as lon, 
		ST_y(geom) as lat 
		from idot_snowplow_current WHERE valid > (now() - '1 hour'::interval)
		and airtemp > -50");

for ($i=0; $row=@pg_fetch_assoc($rs,$i); $i++){
	echo sprintf("Object: %s,%s\n"
  ." Threshold: 999\n"
  ." Text:  -17, 13, 1, \" %.0f \"\n"
 ."End:\n"
	."\n", $row["lat"], $row["lon"], $row["airtemp"]);
}


?>