<?php
/* Generate a KML file of a network locations, yummy */
require_once 'Zend/Json.php';
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/network.php");
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

echo Zend_Json::encode($ar);
?>
