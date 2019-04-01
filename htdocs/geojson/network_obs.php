<?php
/* Generate a JSON file of network observations */
header("Content-type: application/vnd.geo+json");
require_once "../../config/settings.inc.php";
require_once "../../include/database.inc.php";
require_once "../../include/network.php";
require_once "../../include/mlib.php";
require_once "../../include/forms.php";

$network = isset($_REQUEST["network"]) ? $_REQUEST["network"] : "IA_ASOS"; 
$callback = isset($_REQUEST["callback"]) ? $_REQUEST["callback"] : null; 

// TODO: migrate this to explicit backend
$jdata = file_get_contents("http://iem.local/api/1/currents.json?network=$network");
$jobj = json_decode($jdata, $assoc=TRUE);

$mydata = Array();

while ( list($bogus, $iemob) = each($jobj["data"]) ){
    $key = $iemob["station"];
    $mydata[$key] = $iemob;
    unset($mydata[$key]['local_max_sknt_ts']);
    unset($mydata[$key]['local_max_gust_ts']);
    unset($mydata[$key]['day']);
    $mydata[$key]["valid"] = $iemob["utc_valid"];
    $mydata[$key]["sname"] = $iemob["name"];
    $mydata[$key]["sped"] = $mydata[$key]["sknt"] * 1.15078;
    $mydata[$key]["relh"] = relh(f2c($mydata[$key]["tmpf"]), f2c($mydata[$key]["dwpf"]));
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
	echo sprintf("%s(%s);", xssafe($callback), json_encode($ar));
} else{
	echo json_encode($ar);
}
?>