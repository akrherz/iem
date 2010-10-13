<?php
/* Generate a KML file of a network locations, yummy */
require_once 'Zend/Json.php';
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/network.php");
$network = isset($_REQUEST["network"]) ? $_REQUEST["network"] : "KCCI"; 
$nt = new NetworkTable($network);

$ar = Array("type"=>"FeatureCollection",
      "crs" => Array("type"=>"EPSG", 
                     "properties" => Array("code"=>4326,
                                  "coordinate_order" => Array(1,0))),
      "features" => Array()
);

while (list($sid,$data) = each($nt->table))
{
  $z = Array("type"=>"Feature", "id"=>$sid, 
             "properties"=>Array(
                "sname"=> $data["name"],
                "sid"=> $data["id"],
              ),
             "geometry"=>Array("type"=>"Point",
                         "coordinates"=>Array($data["lon"],$data["lat"])));
  $ar["features"][] = $z;
}

echo Zend_Json::encode($ar);
?>
