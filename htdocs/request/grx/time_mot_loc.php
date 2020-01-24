<?php
/*
 * Generate a GR placefile with TIME..MOT..LOC values 
 * $Id: $:
 */
include("../../../config/settings.inc.php");
include_once "../../../include/database.inc.php";
$plimit = isset($_GET["all"]) ? "('TO','SV')" : "('TO')";
$title = isset($_GET["all"]) ? "SVR+TOR" : "TOR";
$pgconn = iemdb('postgis');
$rs = pg_query($pgconn, "SELECT ST_x(tml_geom) as lon, ST_y(tml_geom) as lat,
	ST_AsText(tml_geom_line) as line,
	tml_valid at time zone 'UTC' as tmlv, tml_direction, tml_sknt, 
	polygon_end at time zone 'UTC' as pe, eventid, wfo, phenomena
	 from sbw_". date("Y") ." 
	WHERE polygon_end > now() and phenomena in $plimit and status != 'CAN'");

header( 'Content-type: text/plain');


putenv("TZ=GMT");

echo "RefreshSeconds: 60
Threshold: 999
Title: NWS $title Warning Time-Mot-Loc 
Font: 1, 11, 1, \"Courier New\" 

";

for ($k=0;$row=pg_fetch_array($rs);$k++){
	$valid = strtotime($row["tmlv"]);
	$pe = strtotime($row["pe"]);
	$dur = $pe - $valid;
	$min = $dur/60;
	$spd = floatval($row["tml_sknt"]) * 0.514444444;
	$dir = floatval($row["tml_direction"]);
	$descript = sprintf("%s/%s", $dir, $row["tml_sknt"]);
	$distance = $spd * $dur;

	/* Some magic if we have a line or a string! */
	$lats = Array();
	$lons = Array();
	if ($row["lat"]){
		$lats[] = floatval($row["lat"]);
		$lons[] = floatval($row["lon"]);
	} else if ($row["line"]){
		preg_match_all('/(?P<lon>[0-9\.\-]+) (?P<lat>[0-9\.\-]+)/', 
					$row["line"], $matches);
		$lats = $matches["lat"];
		$lons = $matches["lon"];
		echo "Color: 255 255 0 100\n";
		echo "Polygon:\n";
		$two = "";
		for($m=sizeof($lats)-1; $m > -1; $m--){
			echo sprintf("%s,%s\n", $lats[$m], $lons[$m]);
	  		$lon2 = round($lons[$m] + (($distance * cos(deg2rad(270-$dir)))/(111325 * cos(deg2rad($lats[$m])))),6);
	  		$lat2 = round($lats[$m] + (($distance * sin(deg2rad(270-$dir)))/111325),6);
			$two = sprintf("%s,%s\n%s", $lat2, $lon2, $two);
		}
		echo $two;
		echo "End:\n";
		
	}
	reset($lats);
	for($m=0; $m < sizeof($lats); $m++){
		$lat1 = $lats[$m];
		$lon1 = $lons[$m];
		if ($row["phenomena"] == 'SV'){
			echo "Color: 255 255 0\n";
		} else {
			echo "Color: 255 0 0\n";
		}
	  $lon2 = round($lon1 + (($distance * cos(deg2rad(270-$dir)))/(111325 * cos(deg2rad($lat1)))),6);
	  $lat2 = round($lat1 + (($distance * sin(deg2rad(270-$dir)))/111325),6);

	  echo "Line: 2,0,\"NWS Warning Track (". $row["wfo"] ."-". $row["phenomena"] 
	."-". $row["eventid"].")\\n".$descript."\"
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
	
	echo "Threshold: 999\n\n";
	}
}
?>