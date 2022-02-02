<?php
/* 
 * Generate GeoJSON Convective Sigmets
 */
header("Content-type: application/vnd.geo+json");
require_once "../../config/settings.inc.php";
require_once "../../include/database.inc.php";
require_once "../../include/vtec.php";
$postgis = iemdb("postgis");

$rs = pg_query("SET TIME ZONE 'UTC'");
$rs = pg_prepare($postgis, "SELECT", "SELECT *, 
      ST_asGeoJson(geom) as geojson
      FROM sigmets_current WHERE sigmet_type = 'C' and expire > now() ");

$rs = pg_execute($postgis, "SELECT", Array());


$ar = Array(
  "type"=>"FeatureCollection",
  "features" => Array()
);

$reps = Array();
$subs = Array();

for ($i=0;$row=pg_fetch_array($rs);$i++)
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
echo str_replace($reps, $subs, json_encode($ar));
?>