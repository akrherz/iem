<?php
/* Giveme JSON data listing products */
require_once 'Zend/Json.php';
require_once '../../config/settings.inc.php';
require_once "../../include/database.inc.php";
header("Content-type: application/json");
$connect = iemdb("postgis");
pg_exec($connect, "SET TIME ZONE 'GMT'");

$year = isset($_GET["year"]) ? intval($_GET["year"]) : 2006;
if ($year < 1986 || $year > intval(gmdate("Y"))){
	$ar = Array("error" => "Invalid year specified");
	echo Zend_Json::encode($ar);
	die();
}
$wfo = isset($_GET["wfo"]) ? substr($_GET["wfo"],0,3) : "MPX";
$phenomena = isset($_GET["phenomena"]) ? substr($_GET["phenomena"],0,2) : "SV";
$significance = isset($_GET["significance"]) ? substr($_GET["significance"],0,1) : "W";


$sql = <<<EOF
 select round(sum(ST_area(ST_transform(u.geom,2163)) / 1000000.0)::numeric,0) as area, 
 string_agg( u.name || ' ['||u.state||']', ', ') as locations, eventid,
 min(issue) as issued, max(expire) as expired from warnings_$year w JOIN ugcs u
 ON (u.gid = w.gid) WHERE w.wfo = '$wfo' and
 significance = '$significance' and phenomena = '$phenomena' 
 and eventid is not null GROUP by eventid ORDER by eventid ASC
EOF;
if (($phenomena == "SV" || $phenomena == "TO" || $phenomena == "FF" || $phenomena == "MA") && $significance == "W" && $year > 2003){

$sql = <<<EOF
 WITH countybased as (
 select string_agg( u.name || ' ['||u.state||']', ', ') as locations, eventid,
 min(issue) as issued, max(expire) as expired from warnings_$year w JOIN ugcs u
 ON (u.gid = w.gid) WHERE w.wfo = '$wfo' and
 significance = '$significance' and phenomena = '$phenomena' 
 and eventid is not null GROUP by eventid ),
 
 stormbased as (
 	SELECT round((ST_area(ST_transform(geom,2163)) / 1000000.0)::numeric,0) as area,
 	eventid from sbw_$year w WHERE w.wfo = '$wfo' and
 	significance = '$significance' and phenomena = '$phenomena' 
 	and eventid is not null)
 			
 SELECT s.area, c.locations, c.eventid, issued, expired from 
 stormbased s JOIN countybased c on (c.eventid = s.eventid)
EOF;
}


$result = pg_exec($connect, $sql);

$ar = Array("products" => Array() );
for( $i=0; $z = @pg_fetch_assoc($result,$i); $i++)
{
  $z["id"] = $i +1;
  $z["phenomena"] = $phenomena;
  $z["significance"] = $significance;
  $z["wfo"] = $wfo;
  $z["year"] = $year;
  $z["issued"] = substr($z["issued"],0,16);
  $z["expired"] = substr($z["expired"],0,16);
  $ar["products"][] = $z;
}

echo Zend_Json::encode($ar);

?>
