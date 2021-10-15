<?php 
/*
 * Simple service to return a listing of SHEF variables for a given NWSLI
 * 
 * Currently called by /DCP/plot.phtml
 */
header('Content-type: application/json; charset=utf-8');
require_once "../../config/settings.inc.php";
require_once "../../include/database.inc.php";
require_once "../../include/forms.php";

$hads = iemdb('hads');
$table = sprintf("raw%s_%s", date("Y"), date("m"));
$rs = pg_prepare(
    $hads,
    "SELECT",
    "SELECT distinct key from $table WHERE station = $1"
);

$station = isset($_REQUEST["station"]) ? strtoupper($_REQUEST["station"]) : 
			die(json_encode('Please provide a station variable (NWSLI)')); 

$rs = pg_execute($hads, "SELECT", Array($station));

$ar = Array("vars"=> Array());

for ($i=0;$row=pg_fetch_assoc($rs);$i++)
{
  $z = Array("id"=>$row["key"]);
  $ar["vars"][] = $z;
}

$json = json_encode($ar);

// JSON if no callback
if( ! isset($_REQUEST['callback']))
	exit( $json );

$cb = xssafe($_REQUEST['callback']);
echo "{$cb}($json)";

?>