<?php
/* Giveme JSON data for zones affected by warning */
require_once '../../config/settings.inc.php';
require_once "../../include/database.inc.php";

$ref = isset($_SERVER["HTTP_REFERER"]) ? $_SERVER["HTTP_REFERER"] : 'none';
openlog("iem", LOG_PID | LOG_PERROR, LOG_LOCAL1);
syslog(LOG_WARNING, "Deprecated ". $_SERVER["REQUEST_URI"] .
    ' remote: '. $_SERVER["REMOTE_ADDR"] .
    ' referer: '. $ref);
closelog();


$connect = iemdb("postgis");
pg_exec($connect, "SET TIME ZONE 'GMT'");

$year = isset($_GET["year"]) ? intval($_GET["year"]) : 2006;
$wfo = isset($_GET["wfo"]) ? substr($_GET["wfo"],0,3) : "MPX";
$eventid = isset($_GET["eventid"]) ? intval($_GET["eventid"]) : 103;
$phenomena = isset($_GET["phenomena"]) ? substr($_GET["phenomena"],0,2) : "SV";
$significance = isset($_GET["significance"]) ? substr($_GET["significance"],0,1) : "W";


$sql = "SELECT w.ugc, status, name,
	to_char(issue, 'YYYY-MM-DDThh24:MI:SSZ') as iso_issued,
 	to_char(expire, 'YYYY-MM-DDThh24:MI:SSZ') as iso_expired,
 	to_char(product_issue, 'YYYY-MM-DDThh24:MI:SSZ') as iso_product_issued,
 	to_char(init_expire, 'YYYY-MM-DDThh24:MI:SSZ') as iso_init_expired 
        from warnings_$year w JOIN ugcs u on (u.gid = w.gid) 
        WHERE w.wfo = '$wfo' and 
        w.phenomena = '$phenomena' and w.eventid = $eventid and 
        w.significance = '$significance'";


$result = pg_exec($connect, $sql);

$ar = Array("ugcs" => Array() );
for( $i=0; $z = pg_fetch_assoc($result); $i++)
{
  $z["id"] = $i +1;
  $z["issued"] = $z["iso_issued"];
  $z["expired"] = $z["iso_expired"];
  $z["product_issued"] = $z["iso_product_issued"];
  $z["init_expired"] = $z["iso_init_expired"];
  $ar["ugcs"][] = $z;
}

header("Content-type: application/json");
echo json_encode($ar);

?>