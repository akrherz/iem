<?php header('content-type: application/json; charset=utf-8');
/*
 * JSON Service for state UGC codes
 */
require_once 'Zend/Json.php';
require_once '../../config/settings.inc.php';
require_once "$rootpath/include/database.inc.php";
$dbconn = iemdb('postgis');
$rs = pg_prepare($dbconn, "SELECT", "SELECT ugc, name " .
		"from nws_ugc WHERE state = $1 and ugc is not null and name is not null ORDER by name ASC");

$st = isset($_REQUEST["state"]) ? $_REQUEST["state"] : 'IA';

$rs = pg_execute($dbconn, "SELECT", Array($st));

$ar = Array("ugcs" => Array() );
for( $i=0; $row = @pg_fetch_assoc($rs,$i); $i++){
  $ar["ugcs"][] = $row;
}
$json = Zend_Json::encode($ar);

# JSON if no callback
if( ! isset($_GET['callback']))
	exit( $json );

exit( "{$_GET['callback']}($json)" );
?>
