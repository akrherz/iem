<?php 
/* 
 * JSONP service for IEM Tracked network metadata
 */
header('content-type: application/json; charset=utf-8');
require_once 'Zend/Json.php';
include("../../config/settings.inc.php");
include("../../include/database.inc.php");
include("../../include/network.php");
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

$json = Zend_Json::encode($ar);

# JSON if no callback
if( ! isset($_REQUEST['callback']))
	exit( $json );

exit( "{$_REQUEST['callback']}($json)" );
?>
