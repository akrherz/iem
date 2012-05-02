<?php
/*
 * Generate a GR placefile with TIME..MOT..LOC values 
 * $Id: $:
 */
include("../../../config/settings.inc.php");
include_once "$rootpath/include/database.inc.php";
$pgconn = iemdb('postgis');
$rs = pg_query($pgconn, "SELECT x(tml_geom) as lon, y(tml_geom) as lat,
	tml_valid at time zone 'UTC' as tmlv, tml_direction, tml_sknt, 
	polygon_end at time zone 'UTC' as pe from sbw_". date("Y") ." 
	WHERE polygon_end > 'TODAY' and phenomena = 'TO' 
	and tml_valid is not null");

header( 'Content-type: text/plain');


putenv("TZ=GMT");

echo "RefreshSeconds: 60
Threshold: 999
Title: NWS Tornado Time-Mot-Loc 
Color: 255 0 0
Font: 1, 11, 1, \"Courier New\" 

";

for ($k=0;$row=@pg_fetch_array($rs,$k);$k++){
	$valid = strtotime($row["tmlv"]);
	$pe = strtotime($row["pe"]);
	
	$dur = $pe - $valid;
	$min = $dur/60;
	$spd = floatval($row["tml_sknt"]) * 0.514444444;
	$dir = floatval($row["tml_direction"]);
	$lat1 = floatval($row["lat"]);
	$lon1 = floatval($row["lon"]);
	$distance = $spd * $dur;
	$lon2 = round($lon1 + (($distance * cos(deg2rad(270-$dir)))/(111325 * cos(deg2rad($lat1)))),6);
	$lat2 = round($lat1 + (($distance * sin(deg2rad(270-$dir)))/111325),6);

	echo "Line: 2,0,\"NWS Tornado Track\"
  ".$lat1.",".$lon1."
  ".$lat2.",".$lon2."
End:

";

	echo "Color: 255 255 255\nThreshold:10\n\n";

	for($i=0;$i<=$min;$i++){
		$now = $valid + ($i * 60);
		$dur = $now - $valid;
		$distance = $spd * $dur;
		$lon2 = round($lon1 + (($distance * cos(deg2rad(270-$dir)))/(111325 * cos(deg2rad($lat1)))),6);
		$lat2 = round($lat1 + (($distance * sin(deg2rad(270-$dir)))/111325),6);
		$t_now = date("Hi\z",$now);
	
		//echo "Object: ".$lat2.",".$lon2."\n  Text: 0,0,1,\"".$t_now."\"\nEnd:\n\n";
		echo "Place: ".$lat2.",".$lon2.",".$t_now."\n";
	}
	
	echo "\nColor: 255 0 0\n";
	echo "Threshold: 999\n\n";
}
?>