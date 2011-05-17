<?php
/*
 * JSON Service for station Table changes
 */
require_once 'Zend/Json.php';
require_once '../../config/settings.inc.php';
require_once "$rootpath/include/database.inc.php";
$dbconn = iemdb('mesosite');
$rs = pg_prepare($dbconn, "SELECT", "SELECT *, x(geom) as lon, y(geom) as lat " .
		"from stations WHERE modified >= $1");

$date = isset($_REQUEST["date"]) ? $_REQUEST["date"] : date('Y-m-d');

$rs = pg_execute($dbconn, "SELECT", Array($date));

$ar = Array("stations" => Array() );
for( $i=0; $row = @pg_fetch_assoc($rs,$i); $i++){
  $ar["stations"][] = $row;
}
echo Zend_Json::encode($ar);
?>