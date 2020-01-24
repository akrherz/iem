<?php
/* Giveme JSON data for LSRs inside a polygon */
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
$wfo = isset($_GET["wfo"]) ? substr($_GET["wfo"],0,3) : "MPX";
$eventid = isset($_GET["eventid"]) ? intval($_GET["eventid"]) : 103;
$phenomena = isset($_GET["phenomena"]) ? substr($_GET["phenomena"],0,2) : "SV";
$significance = isset($_GET["significance"]) ? substr($_GET["significance"],0,1) : "W";
$sbw = isset($_GET['sbw']) ? 1 : 0;


if ($sbw){
$sql = sprintf("SELECT distinct l.* from lsrs l, sbw_%s w WHERE
         l.geom && w.geom and ST_contains(w.geom, l.geom) and l.wfo = '%s' and
         l.valid >= w.issue and l.valid <= w.expire and
         w.wfo = '%s' and w.eventid = '%s' and 
         w.significance = '%s' and w.phenomena = '%s'
         ORDER by l.valid ASC", $year, $wfo, $wfo, $eventid, 
         $significance, $phenomena);
} else {
$sql = <<<EOF
	WITH countybased as (
		SELECT min(issue) as issued, max(expire) as expired
		from warnings_$year w JOIN ugcs u on (u.gid = w.gid)
		WHERE w.wfo = '$wfo' and w.eventid = $eventid and 
		w.significance = '$significance' and w.phenomena = '$phenomena')
		
	SELECT distinct l.* from lsrs l, countybased c WHERE
	l.valid >= c.issued and l.valid < c.expired and
	l.wfo = '$wfo' ORDER by l.valid ASC
EOF;
}

$result = pg_exec($connect, $sql);

$ar = Array("lsrs" => Array() );
for( $i=0; $lsr = pg_fetch_array($result); $i++)
{
  $q = Array();
  $q["id"] = $i +1;
  $q["valid"] = substr($lsr["valid"],0,16);
  $q["event"] = $lsr["typetext"];
  $q["type"] = $lsr["type"];
  $q["magnitude"] = $lsr["magnitude"];
  $q["city"] = $lsr["city"];
  $q["county"] = $lsr["county"];
  $q["remark"] = $lsr["remark"];
  $ar["lsrs"][] = $q;
}
header("Content-type: application/json");
echo json_encode($ar);

?>
