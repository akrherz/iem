<?php
/* Giveme JSON data listing of Sites where it is raining */
require_once 'Zend/Json.php';
require_once '../../config/settings.inc.php';
require_once "$rootpath/include/database.inc.php";
include("$rootpath/include/iemaccess.php");
include("$rootpath/include/iemaccessob.php");
$dbconn = iemdb("iem");

$network = isset($_REQUEST["network"]) ? substr($_REQUEST["network"],0,4): "KCCI";

$ar = Array("type"=>"FeatureCollection",
      "crs" => Array("type"=>"EPSG",
                     "properties" => Array("code"=>4326,
                                  "coordinate_order" => Array(1,0))),
      "features" => Array()
);

$iemdata = Array();
$rs = pg_query($dbconn, "select *, c.pday as ob_pday, x(c.geom) as x, 
  y(c.geom) as y from current c LEFT JOIN summary s USING 
  (station, network) WHERE c.network in ('KCCI','KIMT','KELO') 
  and s.day = 'TODAY'");
for( $i=0; $row = @pg_fetch_array($rs,$i); $i++) {
      $iemdata[$row["station"]] = new IEMAccessOb($row);
}

$rs = pg_prepare($dbconn, "SELECT", "SELECT * from events WHERE 
   event = 'P+' and valid > (now() - '15 minutes'::interval)");
$rs = pg_execute($dbconn, "SELECT", Array());

for($i=0; $row = @pg_fetch_array($rs,$i); $i++)
{
  $iemdata[ $row["station"] ]->db["p15m"] = floatval($row["magnitude"]);
}


while (list($key, $iemob) = each($iemdata) ){
  $row = $iemob->db;
  if (!array_key_exists("p15m",$row)){
  	$row["p15m"] = 0;
  }
  $z = Array("type"=>"Feature", "id"=>$row["station"],
             "properties"=>Array(
               "nwsli" => $row["station"],
               "name" => $row["sname"], 
               "p15m" => floatval($row["p15m"]), 
               "p1h" => floatval($row["phour"]), 
               "p1d" => floatval($row["pday"])
              ),
             "geometry"=>Array("type"=>"Point",
                         "coordinates"=>Array($row["x"],$row["y"])));

  $ar["features"][] = $z;
}

echo Zend_Json::encode($ar);

?>