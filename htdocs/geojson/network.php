<?php
/* Generate a KML file of a network locations, yummy */
header("Content-type: application/vnd.geo+json");
include("../../config/settings.inc.php");
include("../../include/database.inc.php");
include("../../include/network.php");
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
                         "coordinates"=>Array(floatval($data["lon"]),
                         					  floatval($data["lat"]))));
  $ar["features"][] = $z;
}

echo json_encode($ar);
?>
