<?php
/* Generate a JSON file of network observations */
header("Content-type: application/vnd.geo+json");
include("../../config/settings.inc.php");
include("../../include/database.inc.php");
include("../../include/iemaccess.php");
include("../../include/iemaccessob.php");
include("../../include/network.php");
include("../../include/mlib.php");

$network = isset($_REQUEST["network"]) ? $_REQUEST["network"] : "IA_ASOS"; 
$callback = isset($_REQUEST["callback"]) ? $_REQUEST["callback"] : null; 

$iem = new IEMAccess();
$asos = $iem->getNetwork($network);

$nt = new NetworkTable($network);
$cities = $nt->table;

$mydata = Array();

while ( list($key, $iemob) = each($asos) ){
    $mydata[$key] = $iemob->db;
    unset($mydata[$key]['geom']);
    unset($mydata[$key]['max_sknt_ts']);
    unset($mydata[$key]['max_gust_ts']);
    unset($mydata[$key]['day']);
    $mydata[$key]["valid"] = gmstrftime('%Y-%m-%dT%H:%MZ', $iemob->ts);
    $mydata[$key]["sname"] = $cities[$key]["name"];
    $mydata[$key]["lat"] = $cities[$key]["lat"];
    $mydata[$key]["lon"] = $cities[$key]["lon"];
    $mydata[$key]["sped"] = $mydata[$key]["sknt"] * 1.15078;
    $mydata[$key]["relh"] = relh(f2c($mydata[$key]["tmpf"]), f2c($mydata[$key]["dwpf"]) );
    $mydata[$key]["feel"] = feels_like($mydata[$key]["tmpf"], 
       $mydata[$key]["relh"], $mydata[$key]["sped"]);
    if ($mydata[$key]["max_gust"] > $mydata[$key]["max_sknt"]){
      $mydata[$key]["peak"] = $mydata[$key]["max_gust"];
    } else {
      $mydata[$key]["peak"] = $mydata[$key]["max_sknt"];
    }

} // End of while

$ar = Array("type"=>"FeatureCollection",
      "crs" => Array("type"=>"EPSG", 
                     "properties" => Array("code"=>4326,
                                  "coordinate_order" => Array(1,0))),
      "features" => Array()
);

while (list($sid,$data) = each($mydata))
{

  $z = Array("type"=>"Feature", "id"=>$sid, 
             "properties"=>$data,
             "geometry"=>Array("type"=>"Point",
                         "coordinates"=>Array($data["lon"],$data["lat"])));
  $ar["features"][] = $z;
}

if ($callback != null){
	echo sprintf("%s(%s);", $callback, json_encode($ar));
} else{
	echo json_encode($ar);
}
?>
