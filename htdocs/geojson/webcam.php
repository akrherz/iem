<?php
/* Giveme JSON data listing products */
require_once 'Zend/Json.php';
require_once '../../config/settings.inc.php';
require_once "$rootpath/include/database.inc.php";

$ts = isset($_REQUEST["ts"]) ? strtotime($_REQUEST["ts"]) : 0;
$network = isset($_REQUEST["network"]) ? substr($_REQUEST["network"],0,4): "KCCI";

$connect = iemdb("mesosite");

if ($ts > 0){
  $result = pg_exec($connect, sprintf("SELECT *, x(geom) as lon, y(geom) as lat
    from camera_log c, webcams w
    WHERE valid = '%s' and c.cam = w.id and w.network = '%s' ORDER by name ASC", 
    date('Y-m-d H:i', $ts), $network) );
} else {
  $result = pg_exec($connect, "SELECT *, x(geom) as lon, y(geom) as lat
  from camera_current c, webcams w 
  WHERE valid > (now() - '15 minutes'::interval) 
  and c.cam = w.id and w.network = '$network'
  ORDER by name ASC");
}


$ar = Array("type"=>"FeatureCollection",
      "crs" => Array("type"=>"EPSG",
                     "properties" => Array("code"=>4326,
                                  "coordinate_order" => Array(1,0))),
      "features" => Array()
);

for( $i=0; $row = @pg_fetch_array($result,$i); $i++)
{
  if ($ts > 0){
    $url = sprintf("http://mesonet.agron.iastate.edu/archive/data/%s/camera/%s/%s_%s.jpg", gmdate("Y/m/d", $ts), $row["cam"], $row["cam"], gmdate("YmdHi", $ts) );
  } else {
    $url = "http://mesonet.agron.iastate.edu/data/camera/stills/". $row["cam"] .".jpg"; 
  }
  $z = Array("type"=>"Feature", "id"=>$row["id"],
             "properties"=>Array(
               "cid" => $row["id"],
               "name" => $row["name"], 
               "county" => $row["county"], 
               "state" => $row["state"], 
               "url" => $url
              ),
             "geometry"=>Array("type"=>"Point",
                         "coordinates"=>Array($row["lon"],$row["lat"])));

  $ar["features"][] = $z;
}

echo Zend_Json::encode($ar);

?>
