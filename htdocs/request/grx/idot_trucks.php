<?php 
/*
 * Generate GR placefile of IDOT Truck Temperatures
 */
header("Content-type: text/plain");

// Try to get it from memcached
$memcache = new Memcache;
$memcache->connect('iem-memcached', 11211);
$val = $memcache->get("/request/grx/idot_trucks.php");
if ($val){
	die($val);
}
ob_start();

echo 'Title: IDOT Trucks
Refresh: 5
Color: 200 200 255
Font: 1, 11, 1, "Courier New"

';
include("../../../config/settings.inc.php");
include("../../../include/database.inc.php");
$dbconn = iemdb("postgis");

/*
$q = 2;
$rs = pg_query($dbconn, "SELECT label, ST_x(geom) as lon,
		ST_y(geom) as lat
		from idot_dashcam_current WHERE valid > (now() - '1 hour'::interval)");

$s3 = "";
for ($i=0; $row=@pg_fetch_assoc($rs,$i); $i++){
	echo sprintf("IconFile: %s, 320, 240, %.0f, %.0f,\"http://mesonet.agron.iastate.edu/data/camera/idot_trucks/%s.jpg\"\n", 
				$q, 0,0, $row["label"]);
	$s3 .= sprintf("Icon: %.4f,%.4f,000,%s,1\n", 
			$row['lat'], $row['lon'], $q);
	$q += 1;
}
*/

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

//echo $s3;

$memcache->set("/request/grx/idot_trucks.php", ob_get_contents(), false, 300);
ob_end_flush();
?>