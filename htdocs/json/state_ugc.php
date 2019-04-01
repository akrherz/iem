<?php header('content-type: application/json; charset=utf-8');
/*
 * JSON Service for state UGC codes
 */
require_once '../../config/settings.inc.php';
require_once "../../include/database.inc.php";
require_once "../../include/forms.php";

$dbconn = iemdb('postgis');
$rs = pg_prepare($dbconn, "SELECT", "SELECT ugc, name " .
		"from ugcs WHERE substr(ugc,1,2) = $1 and ugc is not null and
		end_ts is null and name is not null ORDER by name ASC");

$st = isset($_REQUEST["state"]) ? $_REQUEST["state"] : 'IA';

$rs = pg_execute($dbconn, "SELECT", Array($st));

$ar = Array("ugcs" => Array() );
for( $i=0; $row = @pg_fetch_assoc($rs,$i); $i++){
  $ar["ugcs"][] = $row;
}
$json = json_encode($ar);

// JSON if no callback
if( ! isset($_REQUEST['callback']))
	exit( $json );

$cb = xssafe($_REQUEST['callback']);
echo "{$cb}($json)";
?>