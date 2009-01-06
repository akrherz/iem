<?php
/* Giveme JSON data for zones affected by warning */
require_once 'Zend/Json.php';
require_once '../../config/settings.inc.php';
require_once "$rootpath/include/database.inc.php";

$connect = iemdb("postgis");
pg_exec($connect, "SET TIME ZONE 'GMT'");

$year = isset($_GET["year"]) ? intval($_GET["year"]) : 2006;
$wfo = isset($_GET["wfo"]) ? substr($_GET["wfo"],0,3) : "MPX";
$eventid = isset($_GET["eventid"]) ? intval($_GET["eventid"]) : 103;
$phenomena = isset($_GET["phenomena"]) ? substr($_GET["phenomena"],0,2) : "SV";
$significance = isset($_GET["significance"]) ? substr($_GET["significance"],0,1) : "W";


$sql = "SELECT w.ugc, issue, expire, status, name 
        from warnings_$year w, nws_ugc u WHERE w.wfo = '$wfo' and 
        w.phenomena = '$phenomena' and w.eventid = $eventid and 
        w.significance = '$significance' and w.gtype = 'C' and
        w.ugc = u.ugc";


$result = pg_exec($connect, $sql);

$ar = Array("ugcs" => Array() );
for( $i=0; $z = @pg_fetch_array($result,$i); $i++)
{
  $z["id"] = $i +1;
  $z["issue"] = substr($z["issue"],0,16);
  $z["expire"] = substr($z["expire"],0,16);
  $ar["ugcs"][] = $z;
}

echo Zend_Json::encode($ar);

?>
