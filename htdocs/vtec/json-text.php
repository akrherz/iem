<?php
/* Giveme JSON data for zones affected by warning 
 * This is used by some random AWS EC2 host to get lastsvs=y 
 * 7 Sep 2020: try again to deprecate
 */
require_once '../../config/settings.inc.php';
require_once "../../include/database.inc.php";

$ref = isset($_SERVER["HTTP_REFERER"]) ? $_SERVER["HTTP_REFERER"] : 'none';
openlog("iem", LOG_PID | LOG_PERROR, LOG_LOCAL1);
syslog(LOG_WARNING, "Deprecated ". $_SERVER["REQUEST_URI"] .
    ' remote: '. $_SERVER["REMOTE_ADDR"] .
    ' referer: '. $ref);
closelog();

$connect = iemdb("postgis");
pg_exec($connect, "SET TIME ZONE 'UTC'");

$year = isset($_GET["year"]) ? intval($_GET["year"]) : 2006;
if ($year == 0) die("ERROR: invalid \$year set");
$wfo = isset($_GET["wfo"]) ? substr($_GET["wfo"],0,3) : "MPX";
$eventid = isset($_GET["eventid"]) ? intval($_GET["eventid"]) : 103;
$phenomena = isset($_GET["phenomena"]) ? substr($_GET["phenomena"],0,2) : "SV";
$significance = isset($_GET["significance"]) ? substr($_GET["significance"],0,1) : "W";
$lastsvs = isset($_GET["lastsvs"]) ? $_GET["lastsvs"] : 'n';

$sql = "SELECT replace(report,'\001','') as report, 
               replace(svs,'\001','') as svs
        from warnings_$year w WHERE w.wfo = '$wfo' and 
        w.phenomena = '$phenomena' and w.eventid = $eventid and 
        w.significance = '$significance' ORDER by length(svs) DESC LIMIT 1";


$result = pg_exec($connect, $sql);

$ar = Array("data" => Array() );
for( $i=0; $row  = pg_fetch_array($result); $i++)
{
  $z = Array();
  $z["id"] = $i +1;
  $z["report"] = preg_replace("/\r\r\n/", "\n",$row["report"]);
  $z["svs"] = Array();
  $tokens = @explode('__', $row["svs"]);
  $lsvs = "";
  foreach($tokens as $key => $val)
  { 
    if ($val == "") continue;
    $lsvs = htmlspecialchars( $val );
    $z["svs"][] = preg_replace("/\r\r\n/", "\n",$lsvs);
  }
  if ($lastsvs == "y"){
    $z["svs"] = preg_replace("/\r\r\n/", "\n",$lsvs);
  }
  $ar["data"][] = $z;
}

header("Content-type: application/json");
echo json_encode($ar);

?>
