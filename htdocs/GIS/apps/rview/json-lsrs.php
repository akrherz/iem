<?php
/* Giveme JSON data for LSRs inside a polygon */
require_once 'Zend/Json.php';
require_once '../../../../config/settings.inc.php';
require_once 'lsrs.php';
require_once 'database.inc.php';

$connect = iemdb("postgis");
pg_exec($connect, "SET TIME ZONE GMT");

$year = isset($_GET["year"]) ? intval($_GET["year"]) : 2006;
$wfo = isset($_GET["wfo"]) ? substr($_GET["wfo"],0,3) : "MPX";
$eventid = isset($_GET["eventid"]) ? intval($_GET["eventid"]) : 103;
$phenomena = isset($_GET["phenomena"]) ? substr($_GET["phenomena"],0,2) : "SV";
$significance = isset($_GET["significance"]) ? substr($_GET["significance"],0,1) : "W";
$sbw = isset($_GET['sbw']) ? 1 : 0;


if ($sbw){
$sql = sprintf("SELECT distinct l.* from lsrs_%s l, warnings_%s w WHERE
         l.geom && w.geom and contains(w.geom, l.geom) and l.wfo = '%s' and
         l.valid >= w.issue and l.valid <= w.expire and
         w.wfo = '%s' and w.gtype = 'P' and w.eventid = '%s' and 
         w.significance = '%s' and w.phenomena = '%s'
         ORDER by l.valid ASC", $year, $year, $wfo, $wfo, $eventid, 
         $significance, $phenomena);
} else {
$sql = sprintf("SELECT distinct l.* from lsrs_%s l, warnings_%s w WHERE
         l.valid >= w.issue and l.valid <= w.expire and
         w.wfo = '%s' and l.wfo = '%s' and w.eventid = '%s' and 
         w.significance = '%s' and w.phenomena = '%s'
         ORDER by l.valid ASC", $year, $year, $wfo, $wfo, $eventid, 
         $significance, $phenomena);
}

$result = pg_exec($connect, $sql);

$ar = Array("lsrs" => Array() );
for( $i=0; $lsr = @pg_fetch_array($result,$i); $i++)
{
  $lsr["id"] = $i +1;
  $lsr["valid"] = substr($lsr["valid"],0,16);
  $lsr["event"] = @$lsr_types[$lsr["type"]]["name"];
  $ar["lsrs"][] = $lsr;
}

echo Zend_Json::encode($ar);

?>
