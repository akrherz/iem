<?php 
/* USED BY /DCP/plot.js :( 
 * JSONP service for IEM Tracked network metadata
 */
header('content-type: application/json; charset=utf-8');
include_once "../../config/settings.inc.php";
include_once "../../include/database.inc.php";
include_once "../../include/network.php";
$network = isset($_REQUEST["network"]) ? $_REQUEST["network"] : "KCCI"; 
$nt = new NetworkTable($network);

$ar = Array("stations"=> Array());

while (list($sid,$data) = each($nt->table))
{
  $z = Array("id"=>$sid, 
             "combo" => sprintf("[%s] %s", $sid, $data["name"]),
              "name"=> $data["name"],
              "lon" => $data["lon"],
              "lat" => $data["lat"]);
  $ar["stations"][] = $z;
}

$json = json_encode($ar);

// JSON if no callback
if( ! isset($_REQUEST['callback']))
	exit( $json );

exit( "{$_REQUEST['callback']}($json)" );
?>