<?php
/* 
 * Generate GeoJSON Convective Sigmets
 */
require_once 'Zend/Json.php';
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/vtec.php");
$postgis = iemdb("postgis");

$rs = pg_query("SET TIME ZONE 'GMT'");
$rs = pg_prepare($postgis, "SELECT", "SELECT *, 
      ST_asGeoJson(geom) as geojson
      FROM sigmets_current WHERE sigmet_type = 'C' and expire > now() ");

$rs = pg_execute($postgis, "SELECT", Array());


$ar = Array("type"=>"FeatureCollection",
      "crs" => Array("type"=>"EPSG", 
                     "properties" => Array("code"=>4326,
                                  "coordinate_order" => Array(1,0))),
      "features" => Array()
);

$reps = Array();
$subs = Array();

for ($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{
  $reps[] = "\"REPLACEME$i\"";
  $subs[] = $row["geojson"];


  $z = Array("type"=>"Feature", "id"=>$i, 
             "properties"=>Array(
                "issue"     => substr($row["issue"],0,16),
                "expire"     => substr($row["expire"],0,16),
                "label"         => $row["label"]
  				),
              
             "geometry"=> "REPLACEME$i");
                         
  $ar["features"][] = $z;
}
echo str_replace($reps, $subs, Zend_Json::encode($ar));
?>
