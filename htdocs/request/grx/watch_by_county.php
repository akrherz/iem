<?php
/*
 * Generate Watch by county placefile
 */
 include("../../../config/settings.inc.php");
 include("$rootpath/include/database.inc.php");
 $dbconn = iemdb("postgis");
 
header("Content-type: text/plain");

 
 $rs = pg_query($dbconn, "select phenomena, eventid, 
 		ST_asText(ST_Multi(ST_union(ST_SnapToGrid(geom,0.0001)))) as g from warnings 
 		WHERE significance = 'A' and phenomena IN ('TO','SV') and 
 		issue <= now() and expire > now() 
 		and substr(ugc,3,1) = 'C' GROUP by phenomena, eventid 
 		ORDER by phenomena ASC");

echo "Refresh: 10\n";
echo "Threshold: 999\n";
echo "Title: SPC Watch by County\n";

for ($i=0;$row=@pg_fetch_array($rs,$i);$i++){
	$geom = $row["g"];
	if ($geom == null){
		continue;
	}
	$geom = str_replace("MULTIPOLYGON(((", "", $geom);
	$geom = str_replace(")))", "", $geom);
	$tokens = preg_split("/\)\),\(\(/", $geom);
    foreach ($tokens as $token){
	    if ($row["phenomena"] == "SV"){
	    	$c = ", 255, 255, 0, 255";
	    } else { 
	    	$c = ", 255, 0, 0, 255";
	    }
	    echo "\n;". $row["phenomena"] ." Watch Number ". $row["eventid"] ."\n";
		echo "Polygon:\n";
		$first = true;
		$tokens2 = preg_split("/,/", $token);
		foreach($tokens2 as $token2){
		
			$parts = preg_split("/ /", $token2);
			$extra = "";
			if ($first){
				$extra = $c;
				$first = false;
			}
			echo sprintf("%s, %s%s\n", $parts[1], $parts[0], $extra);
		}
		echo "End:\n\n";
    }
	
}

?>