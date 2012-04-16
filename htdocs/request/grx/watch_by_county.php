<?php
/*
 * Generate Watch by county placefile
 */
 include("../../../config/settings.inc.php");
 include("$rootpath/include/database.inc.php");
 $dbconn = iemdb("postgis");
 
header("Content-type: text/plain");

 
 $rs = pg_query($dbconn, "select phenomena, eventid, " .
 		"ST_asText(ST_Simplify(ST_multi(ST_union(geom)),0.01)) as g from warnings " .
 		"WHERE significance = 'A' and phenomena IN ('TO','SV') and issue <= now() and expire > now() " .
 		"and ugc ~* 'C' GROUP by phenomena, eventid ORDER by phenomena ASC");

echo "Refresh: 10\n";
echo "Threshold: 999\n";
echo "Title: SPC Watch by County\n";

for ($i=0;$row=@pg_fetch_array($rs,$i);$i++){
	$geom = $row["g"];
	$geom = str_replace("MULTIPOLYGON(((", "", $geom);
	$geom = str_replace(")))", "", $geom);
	$tokens = split(",", $geom);
    
    if ($row["phenomena"] == "SV"){
    	$c = ", 255, 255, 0, 255";
    } else { 
    	$c = ", 255, 0, 0, 255";
    }
    echo "\n;". $row["phenomena"] ." Watch Number ". $row["eventid"] ."\n";
	echo "Polygon:\n";
	$first = true;
	foreach($tokens as $token){
	
		$parts = split(" ", $token);
		$extra = "";
		if ($first){
			$extra = $c;
			$first = false;
		}
		echo sprintf("%s, %s%s\n", $parts[1], $parts[0], $extra);
	}
	echo "End:\n\n";
	
}

?>