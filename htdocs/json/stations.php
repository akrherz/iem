<?php 
/*
 * JSON Service for station Table changes , limit the result to 1000 in order
 * to prevent memory overflows...
 */
header('Content-type: application/json; charset=utf-8');
require_once '../../config/settings.inc.php';
require_once "../../include/database.inc.php";
require_once "../../include/forms.php";

$dbconn = iemdb('mesosite');
$rs = pg_prepare($dbconn, "SELECT",
		"SELECT *, ST_x(geom) as lon, ST_y(geom) as lat ".
		"from stations WHERE modified >= $1 LIMIT 1000");

$date = isset($_REQUEST["date"]) ? $_REQUEST["date"] : date('Y-m-d');

$rs = pg_execute($dbconn, "SELECT", Array($date));

$ar = Array("stations" => Array() );
for( $i=0; $row = pg_fetch_assoc($rs); $i++){
  $ar["stations"][] = $row;
  $ar['stations'][$i]['state'] = ($ar['stations'][$i]['state'] == null) ? ""  : $ar['stations'][$i]['state'];
}

$json = json_encode($ar);

// JSON if no callback
if( ! isset($_REQUEST['callback']))
	exit( $json );

$cb = xssafe($_REQUEST["callback"]);
exit( "{$cb}($json)" );
?>