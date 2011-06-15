<?php 
/* 
 * Generate a placefile for a given VTEC ID!
 */
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/vtec.php");
$connect = iemdb("postgis");

$year = isset($_GET["year"]) ? intval($_GET["year"]) : 2006;
$wfo = isset($_GET["wfo"]) ? substr($_GET["wfo"],0,3) : "MPX";
$eventid = isset($_GET["eventid"]) ? intval($_GET["eventid"]) : 103;
$phenomena = isset($_GET["phenomena"]) ? substr($_GET["phenomena"],0,2) : "SV";
$significance = isset($_GET["significance"]) ? substr($_GET["significance"],0,1) : "W";

$rs = pg_prepare($connect, "SELECT", "SELECT *, ST_AsText(geom) as g, 
           round(area(transform(geom,2163)) / 1000000.0) as psize
           from warnings_$year 
           WHERE wfo = $1 and phenomena = $2 and 
           eventid = $3 and significance = $4
           and gtype = 'P'");

$result = pg_execute($connect, "SELECT", 
                     Array($wfo, $phenomena, $eventid, $significance) );
if (pg_num_rows($result) <= 0) {
    $rs = pg_prepare($connect, "SELECT2", "SELECT *, ST_astext(geom) as g, 
           askml(geom) as kml,
           round(area(transform(geom,2163)) / 1000000.0) as psize,
           length(CASE WHEN svs IS NULL THEN '' ELSE svs END) as sz 
           from warnings_$year 
           WHERE wfo = $1 and phenomena = $2 and 
           eventid = $3 and significance = $4
           and gtype = 'C'");

    $result = pg_execute($connect, "SELECT2", 
               Array($wfo, $phenomena, $eventid, $significance) );
}
$fp = sprintf("%s-%s-%s-%s.txt", $wfo, $phenomena, $significance, $eventid);
 header("Content-type: application/octet-stream");
 header("Content-Disposition: attachment; filename=$fp");
echo "Refresh: 0\n";
echo "Threshold: 999\n";
echo "Title: VTEC $wfo ${phenomena}.${significance} $eventid\n";            
                     
for($i=0;$row=@pg_fetch_array($result,$i);$i++){
	$geom = $row["g"];
	$geom = str_replace("MULTIPOLYGON(((", "", $geom);
	$geom = str_replace(")))", "", $geom);
	$tokens = split(",", $geom);
	$phenomena = $row['phenomena'];
	$significance = $row['significance'];
	echo "\n;". $vtec_phenomena[$phenomena] ." ". $vtec_significance[$significance] ." ". $row["eventid"] ."\n";
	echo "Polygon:\n";
    if ($row["phenomena"] == "SV"){
    	$c = ", 255, 255, 0, 255";
    } else { 
    	$c = ", 255, 0, 0, 255";
    }
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