<?php
/*
 * JSON Service for VTEC events!
 */
require_once 'Zend/Json.php';
require_once '../../config/settings.inc.php';
require_once "$rootpath/include/database.inc.php";
$dbconn = iemdb('postgis');
pg_query($dbconn, "SET TIME ZONE 'GMT'");
$rs = pg_prepare($dbconn, "SELECT", "SELECT issue, eventid, phenomena, significance, expire, " .
		"extract(year from issue) || phenomena || significance || eventid as id, wfo " .
		"from warnings WHERE ugc = $1 ORDER by issue ASC");

$ugc = isset($_REQUEST["ugc"]) ? $_REQUEST["ugc"] : 'IAC001';

$rs = pg_execute($dbconn, "SELECT", Array($ugc));

$ar = Array("events" => Array() );
for( $i=0; $row = @pg_fetch_assoc($rs,$i); $i++){
  $ar["events"][] = Array(
  	"issue" => substr($row["issue"],0,16),
  	"expire" => substr($row["expire"],0,16),
  	"eventid" => $row["eventid"],
    "significance" => $row["significance"],
    "phenomena" => $row["phenomena"],
    "wfo" => $row["wfo"],
  );
}
echo Zend_Json::encode($ar);
?>