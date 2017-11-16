<?php
date_default_timezone_set('UTC');

include "../../include/cow.php";
include "../../include/database.inc.php";

$lt = Array("F" => "Flash Flood", "T" => "Tornado", "D" => "Tstm Wnd Dmg", "H" => "Hail","G" => "Wind Gust", "W" => "Waterspout", "M" => "Marine Tstm Wnd");

$pgconn = iemdb("postgis");

$output = fopen("arx.csv", 'w');
fwrite($output, "VALID,TYPE,MAG,CITY,COUNTY,VERIFY,LEADTIME,LAT,LON,WE_RATIO\n");

$cow = new Cow( $pgconn );
$cow->setLimitTime( mktime(12,0,0,10,1,2007),  mktime(12,0,0,7,1,2014) );
$cow->setHailSize(0.75);
$cow->setLimitType( Array("TO","SV") );
$cow->setLimitLSRType( Array("TO","SV") );
$cow->setLimitWFO( Array("ARX") );
$cow->milk();

reset($cow->lsrs);
while( list($k, $lsr) = each($cow->lsrs)){
	
	$rs = pg_query($pgconn, sprintf("SELECT ST_XMIN(geom), ST_XMAX(geom) from ugcs
			WHERE name = '%s' and state = '%s' and end_ts is null
			and substr(ugc,3,1) = 'C'", $lsr['county'], $lsr['state']));
	if (pg_numrows($rs) < 1){
		echo $lsr["county"] ." -- ". $lsr["state"];
	}
	$row = pg_fetch_assoc($rs, 0);
	$ratio = ($lsr["lon0"] - $row["st_xmin"]) / ($row["st_xmax"] - $row["st_xmin"]);
	
  	fwrite($output, sprintf("%s,%s,%s,%s,%s,%s,%s,%s,%s,%.2f\n", gmdate("m/d/Y H:i", $lsr["ts"]),
  			$lt[$lsr["type"]], $lsr["magnitude"], $lsr["city"], $lsr["county"],
			$lsr["warned"] ? 'T': 'F', $lsr["leadtime"] == "NA" ? "M": $lsr["leadtime"],
			$lsr["lat0"], $lsr["lon0"], $ratio));  	
}
fclose($output);
?>