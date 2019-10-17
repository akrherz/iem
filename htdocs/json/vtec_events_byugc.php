<?php
/*
 * JSON Service for VTEC events!
 */
header('Content-type: application/json; charset=utf-8');
require_once '../../config/settings.inc.php';
require_once "../../include/database.inc.php";
require_once "../../include/forms.php";

$dbconn = iemdb('postgis');
pg_query($dbconn, "SET TIME ZONE 'UTC'");
$ugc = isset($_REQUEST["ugc"]) ? $_REQUEST["ugc"] : 'IAC001';
$sdate = isset($_REQUEST["sdate"]) ? $_REQUEST["sdate"] : '1986/1/1';
$edate = isset($_REQUEST["edate"]) ? $_REQUEST["edate"] : 'TODAY';

$rs = pg_prepare($dbconn, "SELECT", "SELECT 
		to_char(issue, 'YYYY-MM-DDThh24:MI:SSZ') as iso_issued,
        to_char(expire, 'YYYY-MM-DDThh24:MI:SSZ') as iso_expired,
		eventid, phenomena, significance, hvtec_nwsli,
		extract(year from issue) || phenomena || significance || eventid as id, 
		wfo 
		from warnings WHERE ugc = $1 and issue > $2::date 
		and issue < $3::date ORDER by issue ASC");



$rs = pg_execute($dbconn, "SELECT", Array($ugc, $sdate, $edate));

$ar = Array("events" => Array() );
for( $i=0; $row = @pg_fetch_assoc($rs,$i); $i++){
  $ar["events"][] = Array(
  	"issue" => $row["iso_issued"],
  	"expire" => $row["iso_expired"],
      "eventid" => $row["eventid"],
      "hvtec_nwsli" => $row["hvtec_nwsli"],
    "significance" => $row["significance"],
    "phenomena" => $row["phenomena"],
    "wfo" => $row["wfo"],
  );
}

$json = json_encode($ar);

// JSON if no callback
if( ! isset($_REQUEST['callback']))
	exit( $json );

$cb = xssafe($_REQUEST['callback']);
echo "{$cb}($json)";
?>