<?php
/*
 * Generate Watch by county placefile
 */
require_once "../../../config/settings.inc.php";
require_once "../../../include/database.inc.php";
$alpha = isset($_GET["alpha"])? intval($_GET["alpha"]): 255;

$dbconn = iemdb("postgis");
 
header("Content-type: text/plain");

 
 $rs = pg_query($dbconn, "select phenomena, eventid, 
 		ST_asText(ST_Multi(ST_buffer(ST_collect( u.simple_geom ),0))) as g 
 		from warnings w JOIN ugcs u on (u.gid = w.gid) 
 		WHERE significance = 'A' and phenomena IN ('TO','SV') and 
 		issue <= now() and expire > now() 
 		and substr(w.ugc,3,1) = 'C' GROUP by phenomena, eventid 
 		ORDER by phenomena ASC");

echo "Refresh: 10\n";
echo "Threshold: 999\n";
echo "Title: SPC Watch by County\n";

for ($i=0;$row=@pg_fetch_array($rs,$i);$i++){
	$geom = $row["g"];
	if ($geom == null){
		continue;
	}
	//echo $geom ."\n";
	$geom = str_replace("MULTIPOLYGON(((", "", $geom);
	$geom = str_replace(")))", "", $geom);
	$tokens3 = preg_split("/\)\),\(\(/", $geom);
    foreach ($tokens3 as $token3){
	    $tokens = preg_split("/\),\(/", $token3);
        foreach ($tokens as $token){
	    if ($row["phenomena"] == "TO"){
	    	$c = ", 255, 255, 0, ${alpha}";
	    } else { 
	    	$c = ", 219, 112, 147, ${alpha}";
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
    }}
	
}

?>