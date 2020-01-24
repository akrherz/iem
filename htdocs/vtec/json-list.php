<?php
/* Giveme JSON data listing products */
require_once '../../config/settings.inc.php';
require_once "../../include/database.inc.php";
header("Content-type: application/json");
$connect = iemdb("postgis");
pg_exec($connect, "SET TIME ZONE 'UTC'");

$ref = isset($_SERVER["HTTP_REFERER"]) ? $_SERVER["HTTP_REFERER"] : 'none';
openlog("iem", LOG_PID | LOG_PERROR, LOG_LOCAL1);
syslog(LOG_WARNING, "Deprecated ". $_SERVER["REQUEST_URI"] .
    ' remote: '. $_SERVER["REMOTE_ADDR"] .
    ' referer: '. $ref);
closelog();

$year = isset($_GET["year"]) ? intval($_GET["year"]) : 2006;
if ($year < 1986 || $year > intval(gmdate("Y"))){
	$ar = Array("error" => "Invalid year specified");
	echo json_encode($ar);
	die();
}
$wfo = isset($_GET["wfo"]) ? substr($_GET["wfo"],0,3) : "MPX";
$phenomena = isset($_GET["phenomena"]) ? substr($_GET["phenomena"],0,2) : "SV";
$significance = isset($_GET["significance"]) ? substr($_GET["significance"],0,1) : "W";


$sql = <<<EOF
 select round(sum(ST_area(ST_transform(u.geom,2163)) / 1000000.0)::numeric,0) as area, 
 string_agg( u.name || ' ['||u.state||']', ', ') as locations, eventid,
 to_char(min(issue), 'YYYY-MM-DDThh24:MI:SSZ') as iso_issued,
 to_char(max(expire), 'YYYY-MM-DDThh24:MI:SSZ') as iso_expired,
 to_char(min(product_issue), 'YYYY-MM-DDThh24:MI:SSZ') as iso_product_issued,
 to_char(max(init_expire), 'YYYY-MM-DDThh24:MI:SSZ') as iso_init_expired,
 max(hvtec_nwsli) as nwsli, max(fcster) as fcster
 
 from warnings_$year w JOIN ugcs u
 ON (u.gid = w.gid) WHERE w.wfo = '$wfo' and
 significance = '$significance' and phenomena = '$phenomena' 
 and eventid is not null GROUP by eventid ORDER by eventid ASC
EOF;
if (($phenomena == "SV" || $phenomena == "TO" || $phenomena == "FF" || 
	 $phenomena == "MA") && $significance == "W" && $year > 2003){

$sql = <<<EOF
 WITH countybased as (
 	select string_agg( u.name || ' ['||u.state||']', ', ') as locations, eventid,
	min(issue) as issued, max(expire) as expired,
	min(product_issue) as product_issued,
	max(init_expire) as init_expired, max(fcster) as fcster
	from warnings_$year w JOIN ugcs u
 	ON (u.gid = w.gid) WHERE w.wfo = '$wfo' and
 	significance = '$significance' and phenomena = '$phenomena' 
 	and eventid is not null GROUP by eventid ),
 
 stormbased as (
 	SELECT round((ST_area(ST_transform(geom,2163)) / 1000000.0)::numeric,0) as area,
 	eventid from sbw_$year w WHERE w.wfo = '$wfo' and
 	significance = '$significance' and phenomena = '$phenomena' 
 	and eventid is not null and status = 'NEW')
 			
 SELECT s.area, c.locations, c.eventid, null as nwsli,
 to_char(issued, 'YYYY-MM-DDThh24:MI:SSZ') as iso_issued,
 to_char(expired, 'YYYY-MM-DDThh24:MI:SSZ') as iso_expired,
 to_char(product_issued, 'YYYY-MM-DDThh24:MI:SSZ') as iso_product_issued,
 to_char(init_expired, 'YYYY-MM-DDThh24:MI:SSZ') as iso_init_expired,
 c.fcster
 from 
 stormbased s JOIN countybased c on (c.eventid = s.eventid)
 ORDER by c.eventid ASC
EOF;
}


$result = pg_exec($connect, $sql);

$ar = Array("products" => Array() );
for( $i=0; $z = pg_fetch_assoc($result); $i++)
{
  $z["id"] = $i +1;
  $z["phenomena"] = $phenomena;
  $z["significance"] = $significance;
  $z["wfo"] = $wfo;
  $z["year"] = $year;
  $z["issued"] = $z["iso_issued"];
  $z["expired"] = $z["iso_expired"];
  $z["product_issued"] = $z["iso_product_issued"];
  $z["init_expired"] = $z["iso_init_expired"];
  $z["fcster"] = $z["fcster"];
  $ar["products"][] = $z;
}

echo json_encode($ar);

?>
